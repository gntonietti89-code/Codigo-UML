"""Entidad empleado y sus asignaciones de trabajo."""

from decimal import Decimal
from typing import TYPE_CHECKING

from .usuario import Usuario

if TYPE_CHECKING:
    from .departamento import Departamento
    from .proyecto import Proyecto


class Empleado(Usuario):
    """Usuario que puede pertenecer a un departamento y trabajar en proyectos."""

    def __init__(
        self,
        identificador: int,
        nombre: str,
        email: str,
        salario: Decimal,
        departamento: "Departamento | None" = None,
    ) -> None:
        super().__init__(identificador, nombre, email)
        self.set_salario(salario)
        self._departamento = None
        self._proyectos: list["Proyecto"] = []
        if departamento is not None:
            departamento.agregar_empleado(self)

    def get_rol(self) -> str:
        return "Empleado"

    def get_salario(self) -> Decimal:
        return self._salario

    def set_salario(self, salario: Decimal) -> None:
        salario_decimal = Decimal(str(salario))
        if salario_decimal < 0:
            raise ValueError("El salario no puede ser negativo")
        self._salario = salario_decimal

    def get_departamento(self) -> "Departamento | None":
        return self._departamento

    def set_departamento(self, departamento: "Departamento | None") -> None:
        self._departamento = departamento

    def get_proyectos(self) -> tuple["Proyecto", ...]:
        return tuple(self._proyectos)

    def agregar_proyecto(self, proyecto: "Proyecto") -> None:
        if proyecto not in self._proyectos:
            self._proyectos.append(proyecto)
        if self not in proyecto.get_empleados():
            proyecto.agregar_empleado(self)