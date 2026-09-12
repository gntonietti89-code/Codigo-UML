"""Asociacion de un empleado con un proyecto."""

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .empleado import Empleado
    from .proyecto import Proyecto


class Asignado:
    """Representa los datos propios de una asignacion de proyecto."""

    def __init__(
        self,
        fecha_asignacion: date,
        rol: str,
        empleado: "Empleado | None" = None,
        proyecto: "Proyecto | None" = None,
    ) -> None:
        if not isinstance(fecha_asignacion, date):
            raise TypeError("fecha_asignacion debe ser date")
        if not isinstance(rol, str) or not rol.strip():
            raise ValueError("El rol no puede estar vacio")
        self._fecha_asignacion = fecha_asignacion
        self._rol = rol.strip()
        self._empleado = empleado
        self._proyecto = proyecto

    @property
    def fecha_asignacion(self) -> date:
        return self._fecha_asignacion

    @property
    def rol(self) -> str:
        return self._rol

    def get_fecha_asignacion(self) -> date:
        return self._fecha_asignacion

    def get_rol(self) -> str:
        return self._rol

    def get_empleado(self) -> "Empleado | None":
        return self._empleado

    def get_proyecto(self) -> "Proyecto | None":
        return self._proyecto