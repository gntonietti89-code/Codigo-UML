"""Conexion y esquema SQLite del sistema.

La ruta se obtiene desde `PROJECT_DB_PATH` para evitar datos de conexion
hardcodeados. Las consultas de los repositorios usan parametros SQLite y las
transacciones se confirman o revierten como una unidad atomica.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from exceptions import PersistenceError


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "gestion.db"


class Database:
    """Gestiona el ciclo de vida de una conexion SQLite.

    La conexion se abre bajo demanda, activa claves foraneas y devuelve filas
    con acceso por nombre. Los errores de SQLite se traducen a una excepcion
    de infraestructura para no filtrar detalles internos al llamador.
    """

    def __init__(self, database_path: str | os.PathLike[str] | None = None) -> None:
        configured_path = database_path or os.getenv("PROJECT_DB_PATH")
        self._database_path = Path(configured_path) if configured_path else DEFAULT_DB_PATH
        self._connection: sqlite3.Connection | None = None

    @property
    def database_path(self) -> Path:
        """Devuelve la ruta configurada sin exponer la conexion interna."""
        return self._database_path

    def connect(self) -> sqlite3.Connection:
        """Abre la conexion y configura el modo seguro de SQLite."""
        # [IA-Generated] La conexion unica evita fugas de recursos y activa FK.
        if self._connection is not None:
            return self._connection
        try:
            self._database_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self._database_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            return self._connection
        except (OSError, sqlite3.Error) as error:
            self._connection = None
            raise PersistenceError("No se pudo abrir la base de datos") from error

    def initialize_schema(self) -> None:
        """Crea las tablas requeridas de forma idempotente."""
        # [IA-Generated] Esquema relacional con integridad referencial.
        schema = """
        CREATE TABLE IF NOT EXISTS departamentos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
            gerente_id INTEGER,
            FOREIGN KEY (gerente_id) REFERENCES empleados(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
            email TEXT NOT NULL UNIQUE CHECK (instr(email, '@') > 1),
            direccion TEXT NOT NULL DEFAULT '',
            telefono TEXT NOT NULL DEFAULT '',
            salario TEXT NOT NULL CHECK (CAST(salario AS REAL) >= 0),
            fecha_inicio TEXT NOT NULL DEFAULT '1970-01-01',
            departamento_id INTEGER,
            FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL CHECK (length(trim(nombre)) > 0),
            descripcion TEXT NOT NULL DEFAULT '',
            presupuesto TEXT NOT NULL CHECK (CAST(presupuesto AS REAL) >= 0),
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            departamento_id INTEGER,
            FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS empleado_proyecto (
            empleado_id INTEGER NOT NULL,
            proyecto_id INTEGER NOT NULL,
            fecha_asignacion TEXT NOT NULL DEFAULT '1970-01-01',
            rol TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (empleado_id, proyecto_id),
            FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS registros_tiempo (
            id INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL,
            horas TEXT NOT NULL CHECK (CAST(horas AS REAL) > 0),
            descripcion TEXT NOT NULL DEFAULT '',
            tarifa_hora TEXT NOT NULL CHECK (CAST(tarifa_hora AS REAL) >= 0),
            empleado_id INTEGER NOT NULL,
            proyecto_id INTEGER NOT NULL,
            FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
        );
        """
        connection = self.connect()
        try:
            connection.executescript(schema)
            self._ensure_column(connection, "departamentos", "gerente_id", "INTEGER")
            self._ensure_column(connection, "empleados", "direccion", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(connection, "empleados", "telefono", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(
                connection,
                "empleados",
                "fecha_inicio",
                "TEXT NOT NULL DEFAULT '1970-01-01'",
            )
            self._ensure_column(connection, "proyectos", "descripcion", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(
                connection,
                "proyectos",
                "estado",
                "TEXT NOT NULL DEFAULT 'Pendiente'",
            )
            self._ensure_column(
                connection,
                "empleado_proyecto",
                "fecha_asignacion",
                "TEXT NOT NULL DEFAULT '1970-01-01'",
            )
            self._ensure_column(connection, "empleado_proyecto", "rol", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(
                connection,
                "registros_tiempo",
                "descripcion",
                "TEXT NOT NULL DEFAULT ''",
            )
            connection.commit()
        except sqlite3.Error as error:
            connection.rollback()
            raise PersistenceError("No se pudo inicializar el esquema") from error

    @staticmethod
    def _ensure_column(
        connection: sqlite3.Connection,
        table: str,
        column: str,
        definition: str,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Ejecuta operaciones atomicas con rollback ante errores de SQLite.

        Centralizar la transaccion evita dejar datos parciales cuando una
        operacion CRUD falla y convierte el error tecnico en PersistenceError.
        """
        # [IA-Refactored] El contexto concentra commit, rollback y traduccion.
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except sqlite3.Error as error:
            connection.rollback()
            raise PersistenceError("La transaccion de base de datos fallo") from error

    def close(self) -> None:
        """Cierra la conexion si estaba abierta."""
        if self._connection is not None:
            try:
                self._connection.close()
            except sqlite3.Error as error:
                raise PersistenceError("No se pudo cerrar la base de datos") from error
            finally:
                self._connection = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exception_type: object, exception: object, traceback: object) -> None:
        self.close()