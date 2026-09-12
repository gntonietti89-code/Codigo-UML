"""Entidad empleado y sus asignaciones de trabajo."""

from decimal import Decimal
from datetime import date
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
        direccion: str = "",
        telefono: str = "",
        fecha_inicio: date | None = None,
    ) -> None:
        if (
            isinstance(salario, str)
            and isinstance(departamento, str)
            and isinstance(direccion, (Decimal, int, float))
            and isinstance(telefono, date)
        ):
            salario, departamento, direccion, telefono, fecha_inicio = (
                direccion,
                None,
                salario,
                departamento,
                telefono,
            )
        super().__init__(identificador, nombre, email)
        self.set_salario(salario)
        self._direccion = direccion
        self._telefono = telefono
        self._fecha_inicio = fecha_inicio
        self._departamento = None
        self._proyectos: list["Proyecto"] = []
        if departamento is not None:
            departamento.agregar_empleado(self)

    @property
    def direccion(self) -> str:
        return self._direccion

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def fecha_inicio(self) -> date | None:
        return self._fecha_inicio

    def puede_acceder(self, modulo: str) -> bool:
        if not isinstance(modulo, str) or not modulo.strip():
            raise ValueError("El modulo no puede estar vacio")
        return self.is_activo()

    def get_rol(self) -> str:
        return "Empleado"

    def get_salario(self) -> Decimal:
        return self._salario

    def set_salario(self, salario: Decimal) -> bool:
        salario_decimal = Decimal(str(salario))
        if salario_decimal < 0:
            raise ValueError("El salario no puede ser negativo")
        self._salario = salario_decimal
        return True

    def get_departamento(self) -> "Departamento | None":
        return self._departamento

    def set_departamento(self, departamento: "Departamento | None") -> None:
        self._departamento = departamento

    def get_proyectos(self) -> tuple["Proyecto", ...]:
        return tuple(self._proyectos)

    def obtener_proyectos(self) -> list["Proyecto"]:
        return list(self._proyectos)

    def registrar_horas(self, registro: "RegistroTiempo") -> bool:
        if registro.get_empleado() is not self:
            return False
        proyecto = registro.get_proyecto()
        if proyecto not in self._proyectos:
            self.agregar_proyecto(proyecto)
        return True

    def agregar_proyecto(self, proyecto: "Proyecto") -> None:
        if proyecto not in self._proyectos:
            self._proyectos.append(proyecto)
        if self not in proyecto.get_empleados():
            proyecto.agregar_empleado(self)