"""Tipos base de usuario del sistema."""

from abc import ABC, abstractmethod


class Usuario(ABC):
    """Clase abstracta que representa a una persona autenticable del sistema."""

    def __init__(self, identificador: int, nombre: str, email: str) -> None:
        self.set_identificador(identificador)
        self.set_nombre(nombre)
        self.set_email(email)
        self._activo = True

    def get_identificador(self) -> int:
        return self._identificador

    def set_identificador(self, identificador: int) -> None:
        if not isinstance(identificador, int) or identificador <= 0:
            raise ValueError("El identificador debe ser un entero positivo")
        self._identificador = identificador

    def get_nombre(self) -> str:
        return self._nombre

    def set_nombre(self, nombre: str) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacio")
        self._nombre = nombre.strip()

    def get_email(self) -> str:
        return self._email

    def set_email(self, email: str) -> None:
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("El email no es valido")
        self._email = email.strip().lower()

    def is_activo(self) -> bool:
        return self._activo

    def set_activo(self, activo: bool) -> None:
        if not isinstance(activo, bool):
            raise TypeError("activo debe ser booleano")
        self._activo = activo

    @abstractmethod
    def get_rol(self) -> str:
        """Devuelve el rol funcional del usuario."""