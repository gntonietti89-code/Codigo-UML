"""Punto de entrada de ejemplo para el sistema de gestion de proyectos."""

from datetime import date
from decimal import Decimal

from modelo import (
    Administrador,
    Departamento,
    Empleado,
    Proyecto,
    RegistroTiempo,
    ReporteManager,
)


def main() -> None:
    """Construye un escenario de ejemplo y muestra un reporte de proyecto."""
    departamento = Departamento(1, "Ingenieria de Software")

    administrador = Administrador(100, "Laura", "laura@empresa.com", nivel_acceso=2)
    administrador.agregar_permiso("gestionar_proyectos")

    empleado = Empleado(
        10,
        "Carlos",
        "carlos@empresa.com",
        Decimal("2800.00"),
        departamento,
    )

    proyecto = Proyecto(
        50,
        "Sistema de reportes",
        Decimal("15000.00"),
        date(2026, 9, 1),
        date(2026, 12, 31),
        departamento,
    )
    empleado.agregar_proyecto(proyecto)

    RegistroTiempo(
        1,
        date(2026, 9, 10),
        Decimal("8.0"),
        Decimal("35.00"),
        empleado,
        proyecto,
    )
    RegistroTiempo(
        2,
        date(2026, 9, 11),
        Decimal("6.5"),
        Decimal("35.00"),
        empleado,
        proyecto,
    )

    resumen = ReporteManager.resumen_proyecto(proyecto)

    print(f"Administrador: {administrador.get_nombre()}")
    print(f"Departamento: {departamento.get_nombre()}")
    print(f"Proyecto: {proyecto.get_nombre()}")
    print(f"Empleado: {empleado.get_nombre()}")
    print(f"Horas totales: {resumen['horas_totales']}")
    print(f"Importe total: {resumen['importe_total']:.2f}")
    print(f"Registros: {resumen['cantidad_registros']}")


if __name__ == "__main__":
    main()