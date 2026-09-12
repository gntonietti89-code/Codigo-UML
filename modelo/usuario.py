"""Tipos base de usuario del sistema."""

from abc import ABC, abstractmethod


class Usuario(ABC):
    """Clase abstracta que representa a una persona autenticable del sistema."""

    def __init__(self, identificador: int, nombre: str, email: str) -> None:
        self.set_id(identificador)
        self.set_nombre(nombre)
        self.set_correo(email)
        self._activo = True

    @property
    def id(self) -> int:
        return self._id

    @property
    def correo(self) -> str:
        return self._correo

    def get_id(self) -> int:
        return self._id

    def set_id(self, identificador: int) -> None:
        if not isinstance(identificador, int) or identificador <= 0:
            raise ValueError("El identificador debe ser un entero positivo")
        self._id = identificador

    def get_identificador(self) -> int:
        return self._id

    def set_identificador(self, identificador: int) -> None:
        self.set_id(identificador)

    def get_nombre(self) -> str:
        return self._nombre

    def set_nombre(self, nombre: str) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacio")
        self._nombre = nombre.strip()

    def get_email(self) -> str:
        return self._email

    def set_email(self, email: str) -> None:
        self.set_correo(email)

    def set_correo(self, correo: str) -> None:
        if not isinstance(correo, str) or "@" not in correo:
            raise ValueError("El correo no es valido")
        self._correo = correo.strip().lower()

    def get_correo(self) -> str:
        return self._correo

    def get_email(self) -> str:
        return self._correo

    def is_activo(self) -> bool:
        return self._activo

    def set_activo(self, activo: bool) -> None:
        if not isinstance(activo, bool):
            raise TypeError("activo debe ser booleano")
        self._activo = activo

    @abstractmethod
    def puede_acceder(self, modulo: str) -> bool:
        """Indica si el usuario puede acceder a un modulo."""