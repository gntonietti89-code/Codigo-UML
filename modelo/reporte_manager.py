"""Servicios de consulta y consolidacion de registros de tiempo."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .empleado import Empleado
    from .proyecto import Proyecto
    from .registro_tiempo import RegistroTiempo


class ReporteManager:
    """Genera totales de horas e importes sin modificar las entidades."""

    @staticmethod
    def obtener_registros(
        proyecto: "Proyecto",
        desde: date | None = None,
        hasta: date | None = None,
    ) -> tuple["RegistroTiempo", ...]:
        if desde is not None and hasta is not None and desde > hasta:
            raise ValueError("desde no puede ser posterior a hasta")
        registros = proyecto.get_registros()
        return tuple(
            registro
            for registro in registros
            if (desde is None or registro.get_fecha() >= desde)
            and (hasta is None or registro.get_fecha() <= hasta)
        )

    @classmethod
    def resumen_proyecto(cls, proyecto: "Proyecto") -> dict[str, Decimal | int]:
        registros = cls.obtener_registros(proyecto)
        return {
            "proyecto_id": proyecto.get_identificador(),
            "horas_totales": sum((registro.get_horas() for registro in registros), Decimal("0")),
            "importe_total": sum((registro.get_importe() for registro in registros), Decimal("0")),
            "cantidad_registros": len(registros),
        }

    @classmethod
    def resumen_empleado(cls, empleado: "Empleado") -> dict[str, Decimal | int]:
        registros = tuple(
            registro
            for proyecto in empleado.get_proyectos()
            for registro in proyecto.get_registros()
            if registro.get_empleado() is empleado
        )
        return {
            "empleado_id": empleado.get_identificador(),
            "horas_totales": sum((registro.get_horas() for registro in registros), Decimal("0")),
            "importe_total": sum((registro.get_importe() for registro in registros), Decimal("0")),
            "cantidad_registros": len(registros),
        }