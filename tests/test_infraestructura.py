import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from api_client import ExternalApiClient
from database import Database
from exceptions import ApiAuthenticationError, ApiBadRequestError, ApiClientError
from modelo import Departamento, Empleado, Proyecto, RegistroTiempo
from repositories import (
    DepartamentoRepository,
    EmpleadoRepository,
    ProyectoRepository,
    RegistroTiempoRepository,
)


class PersistenciaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.database = Database(":memory:")
        self.database.initialize_schema()
        self.departamentos = DepartamentoRepository(self.database)
        self.empleados = EmpleadoRepository(self.database)
        self.proyectos = ProyectoRepository(self.database)
        self.registros = RegistroTiempoRepository(self.database)

    def tearDown(self) -> None:
        self.database.close()

    def test_crud_y_relaciones(self) -> None:
        departamento = Departamento(1, "Calidad")
        empleado = Empleado(1, "Eva", "eva@example.com", Decimal("1800"), departamento)
        proyecto = Proyecto(1, "Auditoria", Decimal("5000"), date(2026, 1, 1), None, departamento)
        registro = RegistroTiempo(1, date(2026, 1, 2), Decimal("2"), Decimal("20"), empleado, proyecto)

        self.departamentos.create(departamento)
        self.empleados.create(empleado)
        self.proyectos.create(proyecto)
        self.proyectos.assign_employee(empleado, proyecto)
        self.registros.create(registro)

        self.assertEqual(self.departamentos.get(1).get_nombre(), "Calidad")
        self.assertEqual(self.empleados.get(1).get_salario(), Decimal("1800"))
        self.assertEqual(self.proyectos.get(1).get_presupuesto(), Decimal("5000"))
        self.assertEqual(self.registros.list(1)[0].get_importe(), Decimal("40"))
        self.assertTrue(self.registros.delete(1))
        self.assertIsNone(self.registros.get(1))


class ApiClientTest(unittest.TestCase):
    def test_envia_token_y_procesa_json(self) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {"id": 1}
        session = Mock()
        session.request.return_value = response

        client = ExternalApiClient("https://api.test", token="secret", session=session)

        self.assertEqual(client.get_resource(1), {"id": 1})
        self.assertEqual(session.request.call_args.kwargs["headers"]["Authorization"], "Bearer secret")

    def test_traduce_estados_http_y_rechaza_entrada(self) -> None:
        session = Mock()
        client = ExternalApiClient("https://api.test", session=session)
        session.request.return_value = Mock(status_code=401)
        with self.assertRaises(ApiAuthenticationError):
            client.get_resource(1)
        session.request.return_value = Mock(status_code=400)
        with self.assertRaises(ApiBadRequestError):
            client.search_users("ana")
        with self.assertRaises(ValueError):
            client.search_users("ana\nDROP")

    def test_json_invalido_se_convierte_en_error_controlado(self) -> None:
        response = Mock(status_code=200)
        response.json.side_effect = ValueError("invalid")
        session = Mock()
        session.request.return_value = response

        with self.assertRaises(ApiClientError):
            ExternalApiClient("https://api.test", session=session).get_resource(1)


if __name__ == "__main__":
    unittest.main()