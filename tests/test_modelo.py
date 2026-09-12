import unittest
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


class ModeloTest(unittest.TestCase):
    def test_relaciones_y_reporte(self) -> None:
        departamento = Departamento(1, "Ingenieria")
        empleado = Empleado(1, "Ana", "ANA@ejemplo.com", Decimal("2500"), departamento)
        proyecto = Proyecto(
            10,
            "Migracion",
            Decimal("10000"),
            date(2026, 1, 1),
            date(2026, 12, 31),
            departamento,
        )
        empleado.agregar_proyecto(proyecto)
        RegistroTiempo(1, date(2026, 2, 1), Decimal("8"), Decimal("25"), empleado, proyecto)

        resumen = ReporteManager.resumen_proyecto(proyecto)

        self.assertEqual(empleado.get_email(), "ana@ejemplo.com")
        self.assertIs(empleado.get_departamento(), departamento)
        self.assertIn(proyecto, empleado.get_proyectos())
        self.assertEqual(resumen["horas_totales"], Decimal("8"))
        self.assertEqual(resumen["importe_total"], Decimal("200"))

    def test_administrador_encapsula_permisos(self) -> None:
        administrador = Administrador(2, "Luis", "luis@ejemplo.com")
        administrador.agregar_permiso("gestionar_proyectos")

        permisos = administrador.get_permisos()

        self.assertIn("gestionar_proyectos", permisos)
        with self.assertRaises(AttributeError):
            permisos.add("otro")

    def test_rechaza_fechas_invalidas(self) -> None:
        with self.assertRaises(ValueError):
            Proyecto(1, "Invalido", Decimal("1"), date(2026, 2, 1), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()