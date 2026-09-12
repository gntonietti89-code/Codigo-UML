"""Entidad departamento y su coleccion encapsulada de empleados."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .empleado import Empleado
    from .proyecto import Proyecto


class Departamento:
    """Agrupa empleados y proyectos bajo un nombre identificable."""

    def __init__(self, identificador: int, nombre: str) -> None:
        self.set_identificador(identificador)
        self.set_nombre(nombre)
        self._empleados: list["Empleado"] = []
        self._proyectos: list["Proyecto"] = []
        self._gerente: "Empleado | None" = None

    @property
    def id_departamento(self) -> int:
        return self._identificador

    @property
    def nombre_departamento(self) -> str:
        return self._nombre

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

    def get_empleados(self) -> tuple["Empleado", ...]:
        return tuple(self._empleados)

    def agregar_empleado(self, empleado: "Empleado") -> bool:
        if empleado is None:
            return False
        if empleado not in self._empleados:
            self._empleados.append(empleado)
        if empleado.get_departamento() is not self:
            empleado.set_departamento(self)
        return True

    def quitar_empleado(self, empleado: "Empleado") -> None:
        if empleado in self._empleados:
            self._empleados.remove(empleado)
            if empleado.get_departamento() is self:
                empleado.set_departamento(None)

    def remover_empleado(self, empleado: "Empleado") -> bool:
        if empleado not in self._empleados:
            return False
        self.quitar_empleado(empleado)
        if self._gerente is empleado:
            self._gerente = None
        return True

    def listar_empleados(self) -> list["Empleado"]:
        return list(self._empleados)

    def asignar_gerente(self, empleado: "Empleado | None") -> bool:
        if empleado is not None and empleado not in self._empleados:
            return False
        self._gerente = empleado
        return True

    def get_gerente(self) -> "Empleado | None":
        return self._gerente

    def get_proyectos(self) -> tuple["Proyecto", ...]:
        return tuple(self._proyectos)

    def agregar_proyecto(self, proyecto: "Proyecto") -> None:
        if proyecto not in self._proyectos:
            self._proyectos.append(proyecto)
        if proyecto.get_departamento() is not self:
            proyecto.set_departamento(self)