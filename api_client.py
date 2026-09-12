"""Cliente HTTP para consultar una API externa de forma segura.

La URL base y el token se leen desde `EXTERNAL_API_BASE_URL` y
`EXTERNAL_API_TOKEN`. El token nunca se incluye en logs ni en mensajes de
error. Las entradas de texto se normalizan, limitan y rechazan si contienen
caracteres de control antes de enviarse a la API.
"""

from __future__ import annotations

import os
import re
from typing import Any

import requests
from requests import Response, Session

from exceptions import (
    ApiAuthenticationError,
    ApiBadRequestError,
    ApiClientError,
    ApiNotFoundError,
    ApiServerError,
)


class ExternalApiClient:
    """Cliente tipado para recursos JSON de una API HTTP externa.

    Se reutiliza una `Session` para eficiencia y se aplica un timeout por
    defecto a cada llamada para evitar que la aplicacion quede bloqueada.
    La sesion puede inyectarse en pruebas para evitar llamadas reales.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 10.0,
        session: Session | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout debe ser mayor que cero")
        configured_url = base_url or os.getenv(
            "EXTERNAL_API_BASE_URL", "https://jsonplaceholder.typicode.com"
        )
        self._base_url = self._validate_base_url(configured_url)
        self._token = token if token is not None else os.getenv("EXTERNAL_API_TOKEN")
        self._timeout = timeout
        self._session = session or requests.Session()

    def get_resource(self, resource_id: int) -> dict[str, Any]:
        """Obtiene un recurso por identificador validado."""
        if not isinstance(resource_id, int) or resource_id <= 0:
            raise ValueError("resource_id debe ser un entero positivo")
        payload = self._request_json("GET", f"/posts/{resource_id}")
        return self._require_object(payload)

    def search_users(self, query: str) -> list[dict[str, Any]]:
        """Busca usuarios usando un parametro sanitizado y valida JSON."""
        safe_query = self._sanitize_query(query)
        payload = self._request_json("GET", "/users", params={"q": safe_query})
        if isinstance(payload, list):
            return [self._require_object(item) for item in payload]
        if isinstance(payload, dict) and isinstance(payload.get("users"), list):
            return [self._require_object(item) for item in payload["users"]]
        raise ApiClientError("La respuesta de usuarios no tiene un formato valido")

    def _request_json(self, method: str, path: str, **kwargs: Any) -> Any:
        # [IA-Generated] Manejo centralizado de seguridad HTTP y errores.
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        try:
            response = self._session.request(
                method,
                f"{self._base_url}{path}",
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            )
        except requests.exceptions.Timeout as error:
            raise ApiClientError("La API externa supero el tiempo de espera") from error
        except requests.exceptions.ConnectionError as error:
            raise ApiClientError("No se pudo conectar con la API externa") from error
        except requests.exceptions.RequestException as error:
            raise ApiClientError("Fallo inesperado en la solicitud HTTP") from error

        self._raise_for_status(response)
        try:
            return response.json()
        except ValueError as error:
            raise ApiClientError("La API devolvio una respuesta JSON invalida") from error

    @staticmethod
    def _raise_for_status(response: Response) -> None:
        if response.status_code in (200, 201, 204):
            return
        if response.status_code == 400:
            raise ApiBadRequestError("La API rechazo la solicitud")
        if response.status_code == 401:
            raise ApiAuthenticationError("La API rechazo las credenciales")
        if response.status_code == 404:
            raise ApiNotFoundError("El recurso no existe en la API")
        if response.status_code >= 500:
            raise ApiServerError("La API externa informo un error interno")
        raise ApiClientError(f"La API devolvio HTTP {response.status_code}")

    @staticmethod
    def _sanitize_query(query: str) -> str:
        # [IA-Refactored] Rechaza entradas malformadas antes de enviarlas.
        if not isinstance(query, str):
            raise TypeError("query debe ser texto")
        safe_query = query.strip()
        if not safe_query or len(safe_query) > 100:
            raise ValueError("query debe tener entre 1 y 100 caracteres")
        if re.search(r"[\x00-\x1f\x7f]", safe_query):
            raise ValueError("query contiene caracteres no permitidos")
        return safe_query

    @staticmethod
    def _require_object(payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ApiClientError("La API no devolvio un objeto JSON")
        return payload

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        normalized_url = base_url.strip().rstrip("/")
        if not normalized_url.startswith(("https://", "http://")):
            raise ValueError("base_url debe utilizar HTTP o HTTPS")
        if any(character.isspace() for character in normalized_url):
            raise ValueError("base_url no puede contener espacios")
        return normalized_url

    def close(self) -> None:
        """Libera la sesion HTTP subyacente."""
        self._session.close()

    def __enter__(self) -> "ExternalApiClient":
        return self

    def __exit__(self, exception_type: object, exception: object, traceback: object) -> None:
        self.close()