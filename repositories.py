"""Repositorios CRUD sobre SQLite para las entidades del dominio.

Los repositorios mantienen SQL fuera de las clases de dominio, utilizan
parametros en todas las consultas y convierten filas a objetos tipados. Esta
separacion facilita probar el dominio sin una base de datos real.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from database import Database
from exceptions import RecordNotFoundError
from modelo import Asignado, Departamento, Empleado, Proyecto, RegistroTiempo


class DepartamentoRepository:
    """Persistencia CRUD de departamentos."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, departamento: Departamento) -> Departamento:
        # [IA-Generated] SQL parametrizado para evitar inyeccion.
        with self._database.transaction() as connection:
            connection.execute(
                "INSERT INTO departamentos (id, nombre, gerente_id) VALUES (?, ?, ?)",
                (
                    departamento.get_identificador(),
                    departamento.get_nombre(),
                    departamento.get_gerente().get_identificador()
                    if departamento.get_gerente() is not None
                    else None,
                ),
            )
        return departamento

    def get(self, identificador: int) -> Departamento | None:
        connection = self._database.connect()
        row = connection.execute(
            "SELECT id, nombre, gerente_id FROM departamentos WHERE id = ?", (identificador,)
        ).fetchone()
        return self._to_domain(row) if row else None

    def list(self) -> tuple[Departamento, ...]:
        rows = self._database.connect().execute(
            "SELECT id, nombre, gerente_id FROM departamentos ORDER BY id"
        ).fetchall()
        return tuple(self._to_domain(row) for row in rows)

    def update(self, departamento: Departamento) -> Departamento:
        with self._database.transaction() as connection:
            cursor = connection.execute(
                "UPDATE departamentos SET nombre = ?, gerente_id = ? WHERE id = ?",
                (
                    departamento.get_nombre(),
                    departamento.get_gerente().get_identificador()
                    if departamento.get_gerente() is not None
                    else None,
                    departamento.get_identificador(),
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError("Departamento no encontrado")
        return departamento

    def delete(self, identificador: int) -> bool:
        with self._database.transaction() as connection:
            cursor = connection.execute("DELETE FROM departamentos WHERE id = ?", (identificador,))
        return cursor.rowcount > 0

    @staticmethod
    def _to_domain(row: object) -> Departamento:
        values = row
        return Departamento(values["id"], values["nombre"])


class EmpleadoRepository:
    """Persistencia CRUD de empleados."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, empleado: Empleado) -> Empleado:
        departamento_id = (
            empleado.get_departamento().get_identificador()
            if empleado.get_departamento() is not None
            else None
        )
        with self._database.transaction() as connection:
            connection.execute(
                """INSERT INTO empleados
                   (id, nombre, email, direccion, telefono, salario, fecha_inicio, departamento_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    empleado.get_identificador(),
                    empleado.get_nombre(),
                    empleado.get_email(),
                    empleado.direccion,
                    empleado.telefono,
                    str(empleado.get_salario()),
                    empleado.fecha_inicio.isoformat()
                    if empleado.fecha_inicio is not None
                    else "1970-01-01",
                    departamento_id,
                ),
            )
        return empleado

    def get(self, identificador: int) -> Empleado | None:
        row = self._database.connect().execute(
                """SELECT id, nombre, email, direccion, telefono, salario,
                             fecha_inicio, departamento_id
               FROM empleados WHERE id = ?""",
            (identificador,),
        ).fetchone()
        if row is None:
            return None
        departamento = self._get_departamento(row["departamento_id"])
        return Empleado(
            row["id"],
            row["nombre"],
            row["email"],
            Decimal(row["salario"]),
            departamento,
            row["direccion"],
            row["telefono"],
            date.fromisoformat(row["fecha_inicio"]),
        )

    def list(self) -> tuple[Empleado, ...]:
        rows = self._database.connect().execute(
            "SELECT id FROM empleados ORDER BY id"
        ).fetchall()
        return tuple(empleado for row in rows if (empleado := self.get(row["id"])) is not None)

    def update(self, empleado: Empleado) -> Empleado:
        departamento_id = (
            empleado.get_departamento().get_identificador()
            if empleado.get_departamento() is not None
            else None
        )
        with self._database.transaction() as connection:
            cursor = connection.execute(
                     """UPDATE empleados SET nombre = ?, email = ?, direccion = ?,
                         telefono = ?, salario = ?, fecha_inicio = ?, departamento_id = ?
                         WHERE id = ?""",
                (
                    empleado.get_nombre(),
                    empleado.get_email(),
                          empleado.direccion,
                          empleado.telefono,
                    str(empleado.get_salario()),
                          empleado.fecha_inicio.isoformat()
                          if empleado.fecha_inicio is not None
                          else "1970-01-01",
                    departamento_id,
                    empleado.get_identificador(),
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError("Empleado no encontrado")
        return empleado

    def delete(self, identificador: int) -> bool:
        with self._database.transaction() as connection:
            cursor = connection.execute("DELETE FROM empleados WHERE id = ?", (identificador,))
        return cursor.rowcount > 0

    def _get_departamento(self, identificador: int | None) -> Departamento | None:
        if identificador is None:
            return None
        row = self._database.connect().execute(
            "SELECT id, nombre FROM departamentos WHERE id = ?", (identificador,)
        ).fetchone()
        return Departamento(row["id"], row["nombre"]) if row else None


class ProyectoRepository:
    """Persistencia CRUD de proyectos y sus asignaciones."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, proyecto: Proyecto) -> Proyecto:
        departamento_id = (
            proyecto.get_departamento().get_identificador()
            if proyecto.get_departamento() is not None
            else None
        )
        with self._database.transaction() as connection:
            connection.execute(
                """INSERT INTO proyectos
                   (id, nombre, descripcion, presupuesto, fecha_inicio, fecha_fin,
                    estado, departamento_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    proyecto.get_identificador(),
                    proyecto.get_nombre(),
                    proyecto.descripcion,
                    str(proyecto.get_presupuesto()),
                    proyecto.get_fecha_inicio().isoformat(),
                    proyecto.get_fecha_fin().isoformat() if proyecto.get_fecha_fin() else None,
                    proyecto.estado,
                    departamento_id,
                ),
            )
        return proyecto

    def get(self, identificador: int) -> Proyecto | None:
        row = self._database.connect().execute(
                """SELECT id, nombre, descripcion, presupuesto, fecha_inicio, fecha_fin,
                             estado, departamento_id
               FROM proyectos WHERE id = ?""",
            (identificador,),
        ).fetchone()
        if row is None:
            return None
        departamento = self._get_departamento(row["departamento_id"])
        return Proyecto(
            row["id"],
            row["nombre"],
            Decimal(row["presupuesto"]),
            date.fromisoformat(row["fecha_inicio"]),
            date.fromisoformat(row["fecha_fin"]) if row["fecha_fin"] else None,
            departamento,
            row["descripcion"],
            row["estado"],
        )

    def list(self) -> tuple[Proyecto, ...]:
        rows = self._database.connect().execute(
            "SELECT id FROM proyectos ORDER BY id"
        ).fetchall()
        return tuple(proyecto for row in rows if (proyecto := self.get(row["id"])) is not None)

    def update(self, proyecto: Proyecto) -> Proyecto:
        departamento_id = (
            proyecto.get_departamento().get_identificador()
            if proyecto.get_departamento() is not None
            else None
        )
        with self._database.transaction() as connection:
            cursor = connection.execute(
                     """UPDATE proyectos SET nombre = ?, descripcion = ?, presupuesto = ?,
                         fecha_inicio = ?, fecha_fin = ?, estado = ?, departamento_id = ?
                         WHERE id = ?""",
                (
                    proyecto.get_nombre(),
                          proyecto.descripcion,
                    str(proyecto.get_presupuesto()),
                    proyecto.get_fecha_inicio().isoformat(),
                    proyecto.get_fecha_fin().isoformat() if proyecto.get_fecha_fin() else None,
                          proyecto.estado,
                    departamento_id,
                    proyecto.get_identificador(),
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError("Proyecto no encontrado")
        return proyecto

    def delete(self, identificador: int) -> bool:
        with self._database.transaction() as connection:
            cursor = connection.execute("DELETE FROM proyectos WHERE id = ?", (identificador,))
        return cursor.rowcount > 0

    def assign_employee(
        self,
        empleado: Empleado,
        proyecto: Proyecto,
        fecha_asignacion: date | None = None,
        rol: str = "",
    ) -> Asignado:
        asignado = Asignado(fecha_asignacion or date.today(), rol or "Sin definir", empleado, proyecto)
        with self._database.transaction() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO empleado_proyecto
                   (empleado_id, proyecto_id, fecha_asignacion, rol)
                   VALUES (?, ?, ?, ?)""",
                (
                    empleado.get_identificador(),
                    proyecto.get_identificador(),
                    asignado.get_fecha_asignacion().isoformat(),
                    asignado.get_rol(),
                ),
            )
        proyecto.asignar_empleado(empleado)
        return asignado

    def remove_employee(self, empleado: Empleado, proyecto: Proyecto) -> bool:
        with self._database.transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM empleado_proyecto WHERE empleado_id = ? AND proyecto_id = ?",
                (empleado.get_identificador(), proyecto.get_identificador()),
            )
        return cursor.rowcount > 0

    def _get_departamento(self, identificador: int | None) -> Departamento | None:
        if identificador is None:
            return None
        row = self._database.connect().execute(
            "SELECT id, nombre FROM departamentos WHERE id = ?", (identificador,)
        ).fetchone()
        return Departamento(row["id"], row["nombre"]) if row else None


class RegistroTiempoRepository:
    """Persistencia CRUD de registros de tiempo."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, registro: RegistroTiempo) -> RegistroTiempo:
        with self._database.transaction() as connection:
            connection.execute(
                """INSERT INTO registros_tiempo
                   (id, fecha, horas, tarifa_hora, empleado_id, proyecto_id, descripcion)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    registro.get_identificador(),
                    registro.get_fecha().isoformat(),
                    str(registro.get_horas()),
                    str(registro.get_tarifa_hora()),
                    registro.get_empleado().get_identificador(),
                    registro.get_proyecto().get_identificador(),
                    registro.descripcion,
                ),
            )
        return registro

    def get(self, identificador: int) -> RegistroTiempo | None:
        row = self._database.connect().execute(
                """SELECT id, fecha, horas, tarifa_hora, empleado_id, proyecto_id, descripcion
               FROM registros_tiempo WHERE id = ?""",
            (identificador,),
        ).fetchone()
        return self._to_domain(row) if row else None

    def list(self, proyecto_id: int | None = None) -> tuple[RegistroTiempo, ...]:
        query = "SELECT id FROM registros_tiempo"
        parameters: tuple[object, ...] = ()
        if proyecto_id is not None:
            query += " WHERE proyecto_id = ?"
            parameters = (proyecto_id,)
        query += " ORDER BY fecha, id"
        rows = self._database.connect().execute(query, parameters).fetchall()
        return tuple(registro for row in rows if (registro := self.get(row["id"])) is not None)

    def update(self, registro: RegistroTiempo) -> RegistroTiempo:
        with self._database.transaction() as connection:
            cursor = connection.execute(
                     """UPDATE registros_tiempo SET fecha = ?, horas = ?, tarifa_hora = ?,
                         empleado_id = ?, proyecto_id = ?, descripcion = ? WHERE id = ?""",
                (
                    registro.get_fecha().isoformat(),
                    str(registro.get_horas()),
                    str(registro.get_tarifa_hora()),
                    registro.get_empleado().get_identificador(),
                    registro.get_proyecto().get_identificador(),
                    registro.descripcion,
                    registro.get_identificador(),
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError("Registro de tiempo no encontrado")
        return registro

    def delete(self, identificador: int) -> bool:
        with self._database.transaction() as connection:
            cursor = connection.execute("DELETE FROM registros_tiempo WHERE id = ?", (identificador,))
        return cursor.rowcount > 0

    def _to_domain(self, row: object) -> RegistroTiempo:
        empleado_row = self._database.connect().execute(
                """SELECT id, nombre, email, direccion, telefono, salario, fecha_inicio
                    FROM empleados WHERE id = ?""",
                (row["empleado_id"],),
        ).fetchone()
        proyecto_row = self._database.connect().execute(
                """SELECT id, nombre, descripcion, presupuesto, fecha_inicio, fecha_fin, estado
               FROM proyectos WHERE id = ?""",
            (row["proyecto_id"],),
        ).fetchone()
        if empleado_row is None or proyecto_row is None:
            raise RecordNotFoundError("El registro referencia una entidad inexistente")
        empleado = Empleado(
            empleado_row["id"],
            empleado_row["nombre"],
            empleado_row["email"],
            Decimal(empleado_row["salario"]),
            None,
            empleado_row["direccion"],
            empleado_row["telefono"],
            date.fromisoformat(empleado_row["fecha_inicio"]),
        )
        proyecto = Proyecto(
            proyecto_row["id"],
            proyecto_row["nombre"],
            Decimal(proyecto_row["presupuesto"]),
            date.fromisoformat(proyecto_row["fecha_inicio"]),
            date.fromisoformat(proyecto_row["fecha_fin"]) if proyecto_row["fecha_fin"] else None,
            None,
            proyecto_row["descripcion"],
            proyecto_row["estado"],
        )
        return RegistroTiempo(
            row["id"],
            date.fromisoformat(row["fecha"]),
            Decimal(row["horas"]),
            Decimal(row["tarifa_hora"]),
            empleado,
            proyecto,
            row["descripcion"],
        )