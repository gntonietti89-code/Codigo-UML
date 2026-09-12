"""Entidad proyecto y sus empleados y registros de tiempo."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .departamento import Departamento
    from .empleado import Empleado
    from .registro_tiempo import RegistroTiempo


class Proyecto:
    """Trabajo planificado con presupuesto, fechas y esfuerzo registrado."""

    def __init__(
        self,
        identificador: int,
        nombre: str,
        presupuesto: Decimal,
        fecha_inicio: date,
        fecha_fin: date | None = None,
        departamento: "Departamento | None" = None,
        descripcion: str = "",
        estado: str = "Pendiente",
    ) -> None:
        if isinstance(presupuesto, str) and isinstance(fecha_fin, str):
            descripcion, estado = presupuesto, fecha_fin
            presupuesto, fecha_fin = Decimal("0"), None
        self.set_identificador(identificador)
        self.set_nombre(nombre)
        self.set_presupuesto(presupuesto)
        self.set_fecha_inicio(fecha_inicio)
        self.set_fecha_fin(fecha_fin)
        self._descripcion = descripcion
        self._estado = estado
        self._departamento = None
        self._empleados: list["Empleado"] = []
        self._registros: list["RegistroTiempo"] = []
        if departamento is not None:
            departamento.agregar_proyecto(self)

    @property
    def id_proyecto(self) -> int:
        return self._identificador

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def estado(self) -> str:
        return self._estado

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

    def get_presupuesto(self) -> Decimal:
        return self._presupuesto

    def set_presupuesto(self, presupuesto: Decimal) -> None:
        presupuesto_decimal = Decimal(str(presupuesto))
        if presupuesto_decimal < 0:
            raise ValueError("El presupuesto no puede ser negativo")
        self._presupuesto = presupuesto_decimal

    def get_fecha_inicio(self) -> date:
        return self._fecha_inicio

    def set_fecha_inicio(self, fecha_inicio: date) -> None:
        if not isinstance(fecha_inicio, date):
            raise TypeError("fecha_inicio debe ser date")
        self._fecha_inicio = fecha_inicio
        if hasattr(self, "_fecha_fin") and self._fecha_fin is not None and fecha_inicio > self._fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha fin")

    def get_fecha_fin(self) -> date | None:
        return self._fecha_fin

    def set_fecha_fin(self, fecha_fin: date | None) -> None:
        if fecha_fin is not None and not isinstance(fecha_fin, date):
            raise TypeError("fecha_fin debe ser date o None")
        if fecha_fin is not None and hasattr(self, "_fecha_inicio") and fecha_fin < self._fecha_inicio:
            raise ValueError("La fecha fin no puede ser anterior a la fecha de inicio")
        self._fecha_fin = fecha_fin

    def get_departamento(self) -> "Departamento | None":
        return self._departamento

    def set_departamento(self, departamento: "Departamento | None") -> None:
        self._departamento = departamento

    def get_empleados(self) -> tuple["Empleado", ...]:
        return tuple(self._empleados)

    def agregar_empleado(self, empleado: "Empleado") -> None:
        if empleado not in self._empleados:
            self._empleados.append(empleado)
        if self not in empleado.get_proyectos():
            empleado.agregar_proyecto(self)

    def asignar_empleado(self, empleado: "Empleado") -> bool:
        if empleado is None:
            return False
        self.agregar_empleado(empleado)
        return True

    def remover_empleado(self, empleado: "Empleado") -> bool:
        if empleado not in self._empleados:
            return False
        self._empleados.remove(empleado)
        proyectos = getattr(empleado, "_proyectos", [])
        if self in proyectos:
            proyectos.remove(self)
        return True

    def calcular_total_horas(self) -> Decimal:
        return sum((registro.get_horas() for registro in self._registros), Decimal("0"))

    def get_registros(self) -> tuple["RegistroTiempo", ...]:
        return tuple(self._registros)

    def agregar_registro(self, registro: "RegistroTiempo") -> None:
        if registro.get_proyecto() is not self:
            raise ValueError("El registro pertenece a otro proyecto")
        if registro not in self._registros:
            self._registros.append(registro)