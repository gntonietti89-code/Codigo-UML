"""Registro de horas trabajadas por un empleado en un proyecto."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .empleado import Empleado
    from .proyecto import Proyecto


class RegistroTiempo:
    """Representa horas facturables en una fecha y calcula su importe."""

    def __init__(
        self,
        identificador: int,
        fecha: date,
        horas: Decimal,
        tarifa_hora: Decimal | str = Decimal("0"),
        empleado: "Empleado | None" = None,
        proyecto: "Proyecto | None" = None,
        descripcion: str = "",
    ) -> None:
        if isinstance(tarifa_hora, str) and empleado is None and proyecto is None and not descripcion:
            descripcion = tarifa_hora
            tarifa_hora = Decimal("0")
        self.set_identificador(identificador)
        self.set_fecha(fecha)
        self.set_horas(horas)
        self.set_tarifa_hora(tarifa_hora)
        self._descripcion = descripcion
        self._empleado = empleado
        self._proyecto = proyecto
        if proyecto is not None:
            proyecto.agregar_registro(self)

    @property
    def id_registro(self) -> int:
        return self._identificador

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def validar_limite_diario(self) -> bool:
        return self._horas <= Decimal("24")

    def obtener_resumen(self) -> str:
        return f"{self._fecha.isoformat()}: {self._horas} horas - {self._descripcion}".strip()

    def set_identificador(self, identificador: int) -> None:
        if not isinstance(identificador, int) or identificador <= 0:
            raise ValueError("El identificador debe ser un entero positivo")
        self._identificador = identificador

    def get_identificador(self) -> int:
        return self._identificador

    def set_fecha(self, fecha: date) -> None:
        if not isinstance(fecha, date):
            raise TypeError("fecha debe ser date")
        self._fecha = fecha

    def get_fecha(self) -> date:
        return self._fecha

    def set_horas(self, horas: Decimal) -> None:
        horas_decimal = Decimal(str(horas))
        if horas_decimal <= 0:
            raise ValueError("Las horas deben ser mayores que cero")
        self._horas = horas_decimal

    def get_horas(self) -> Decimal:
        return self._horas

    def set_tarifa_hora(self, tarifa_hora: Decimal) -> None:
        tarifa_decimal = Decimal(str(tarifa_hora))
        if tarifa_decimal < 0:
            raise ValueError("La tarifa no puede ser negativa")
        self._tarifa_hora = tarifa_decimal

    def get_tarifa_hora(self) -> Decimal:
        return self._tarifa_hora

    def get_empleado(self) -> "Empleado | None":
        return self._empleado

    def get_proyecto(self) -> "Proyecto | None":
        return self._proyecto

    def get_importe(self) -> Decimal:
        return self._horas * self._tarifa_hora