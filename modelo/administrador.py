"""Entidad administrador del sistema."""

from .usuario import Usuario


class Administrador(Usuario):
    """Usuario con permisos para administrar recursos del sistema."""

    def __init__(
        self,
        identificador: int,
        nombre: str,
        email: str,
        nivel_acceso: int = 1,
    ) -> None:
        super().__init__(identificador, nombre, email)
        self.set_nivel_acceso(nivel_acceso)
        self._permisos: set[str] = set()

    def get_rol(self) -> str:
        return "Administrador"

    def get_nivel_acceso(self) -> int:
        return self._nivel_acceso

    def set_nivel_acceso(self, nivel_acceso: int) -> None:
        if not isinstance(nivel_acceso, int) or nivel_acceso < 1:
            raise ValueError("El nivel de acceso debe ser un entero positivo")
        self._nivel_acceso = nivel_acceso

    def get_permisos(self) -> frozenset[str]:
        return frozenset(self._permisos)

    def agregar_permiso(self, permiso: str) -> None:
        if not isinstance(permiso, str) or not permiso.strip():
            raise ValueError("El permiso no puede estar vacio")
        self._permisos.add(permiso.strip())

    def quitar_permiso(self, permiso: str) -> None:
        self._permisos.discard(permiso)

    def tiene_permiso(self, permiso: str) -> bool:
        return permiso in self._permisos