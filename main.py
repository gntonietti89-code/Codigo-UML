"""Punto de entrada del sistema de gestion de proyectos.

El modo interactivo mantiene los errores de infraestructura dentro del flujo
de la aplicacion: un fallo de red, de SQLite o de validacion no termina el
menu ni muestra credenciales o detalles internos al usuario.
"""

from datetime import date
from decimal import Decimal
import sqlite3
from typing import Callable

import requests

from api_client import ExternalApiClient
from database import Database
from exceptions import ApiClientError, PersistenceError
from modelo import (
    Administrador,
    Departamento,
    Empleado,
    Proyecto,
    RegistroTiempo,
    ReporteManager,
)
from repositories import (
    DepartamentoRepository,
    EmpleadoRepository,
    ProyectoRepository,
    RegistroTiempoRepository,
)


def _build_demo() -> tuple[Administrador, Departamento, Empleado, Proyecto, RegistroTiempo]:
    """Construye un agregado de dominio válido para la demostración."""
    # [IA-Generated] Los modelos validan tipos, fechas y valores monetarios.
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

    registro_inicial = RegistroTiempo(
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

    return administrador, departamento, empleado, proyecto, registro_inicial


def _print_demo() -> None:
    """Muestra el reporte calculado directamente desde objetos de dominio."""
    administrador, departamento, empleado, proyecto, _ = _build_demo()
    resumen = ReporteManager.resumen_proyecto(proyecto)

    print(f"Administrador: {administrador.get_nombre()}")
    print(f"Departamento: {departamento.get_nombre()}")
    print(f"Proyecto: {proyecto.get_nombre()}")
    print(f"Empleado: {empleado.get_nombre()}")
    print(f"Horas totales: {resumen['horas_totales']}")
    print(f"Importe total: {resumen['importe_total']:.2f}")
    print(f"Registros: {resumen['cantidad_registros']}")


def _persist_demo(database: Database) -> None:
    """Guarda un escenario de ejemplo mediante los DAOs tipados.

    Cada repositorio usa consultas parametrizadas y transacciones, por lo que
    la conversion entre objetos del dominio y filas queda aislada de `main`.
    """
    # [IA-Refactored] La persistencia se coordina sin SQL en el punto de entrada.
    proyecto_repository = ProyectoRepository(database)
    if proyecto_repository.get(50) is not None:
        print("El proyecto de ejemplo ya esta persistido.")
        return

    _, departamento, empleado, proyecto, registro = _build_demo()
    DepartamentoRepository(database).create(departamento)
    EmpleadoRepository(database).create(empleado)
    proyecto_repository.create(proyecto)
    proyecto_repository.assign_employee(empleado, proyecto)
    RegistroTiempoRepository(database).create(registro)
    print(f"Proyecto persistido: {proyecto.get_nombre()}")


def _query_external_api() -> None:
    """Consulta un recurso JSON con parametros validados por el cliente HTTP."""
    resource_id = input("ID del recurso HTTP (entero positivo): ").strip()
    if not resource_id.isdigit() or int(resource_id) <= 0:
        print("Entrada invalida: el ID debe ser un entero positivo.")
        return
    with ExternalApiClient() as client:
        resource = client.get_resource(int(resource_id))
    print(f"Respuesta JSON: {resource}")


def _read_choice() -> str:
    """Lee una opcion acotada para evitar errores de conversion de entrada."""
    return input("Selecciona una opcion: ").strip()


def run_interactive() -> None:
    """Ejecuta un menu recuperable para las operaciones principales."""
    database = Database()
    try:
        database.initialize_schema()
        actions: dict[str, Callable[[], None]] = {
            "1": _print_demo,
            "2": lambda: _persist_demo(database),
            "3": _query_external_api,
        }
        while True:
            print("\n1. Mostrar reporte de ejemplo")
            print("2. Persistir ejemplo en SQLite")
            print("3. Consultar API externa")
            print("0. Salir")
            choice = _read_choice()
            if choice == "0":
                print("Programa finalizado.")
                return
            action = actions.get(choice)
            if action is None:
                print("Opcion invalida. Usa 0, 1, 2 o 3.")
                continue
            try:
                action()
            except requests.exceptions.RequestException:
                print("No se pudo completar la solicitud de red.")
            except ApiClientError as error:
                print(f"Error controlado de API: {error}")
            except sqlite3.Error:
                print("No se pudo completar la operacion de base de datos.")
            except PersistenceError as error:
                print(f"Error controlado de persistencia: {error}")
            except (TypeError, ValueError) as error:
                print(f"Datos inconsistentes: {error}")
    finally:
        database.close()


def main(interactive: bool = False) -> None:
    """Inicia el demo o el menu; el modo evita redes por defecto en pruebas."""
    if interactive:
        run_interactive()
        return
    _print_demo()


if __name__ == "__main__":
    main(interactive=True)