"""Excepciones de aplicacion para separar errores tecnicos del dominio."""


class PersistenceError(RuntimeError):
    """Error controlado producido durante una operacion de persistencia."""


class RecordNotFoundError(PersistenceError):
    """Indica que la entidad solicitada no existe."""


class ApiClientError(RuntimeError):
    """Error base para fallos controlados del cliente HTTP."""


class ApiAuthenticationError(ApiClientError):
    """La API rechazo las credenciales proporcionadas."""


class ApiBadRequestError(ApiClientError):
    """La API rechazo los parametros enviados."""


class ApiNotFoundError(ApiClientError):
    """La API no encontro el recurso solicitado."""


class ApiServerError(ApiClientError):
    """La API externa informo un fallo del servidor."""