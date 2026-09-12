# INFRETRO

## 1. Declaración Transparente de Herramientas de IA Utilizadas

Para este proyecto utilicé **GitHub Copilot** y **ChatGPT** como asistentes de código durante el desarrollo. Los empleé para proponer estructuras iniciales, revisar alternativas de diseño, detectar posibles errores y mejorar la documentación técnica.

La Inteligencia Artificial fue utilizada como apoyo y no como sustituto de mi criterio. Revisé las propuestas, las adapté a los modelos de dominio existentes, ejecuté las pruebas automatizadas y comprobé que las decisiones fueran coherentes con los requisitos de persistencia, seguridad y programación orientada a objetos.

## 2. Identificación de Código Generado e Integrado

La IA asistió principalmente en los siguientes componentes:

| Componente | Asistencia recibida | Integración realizada |
|---|---|---|
| `repositories.py` | Estructuras base de repositorios CRUD | Adapté cada repositorio a las clases `Empleado`, `Proyecto`, `Departamento` y `RegistroTiempo`, incluyendo sus relaciones. |
| `database.py` | Diseño inicial del gestor SQLite y del esquema relacional | Revisé las tablas, las claves foráneas, las transacciones y la configuración de la ruta de la base de datos. |
| `api_client.py` | Estructura de las llamadas HTTP y procesamiento JSON | Añadí validación de entradas, timeout, autenticación mediante token y traducción controlada de errores. |
| `main.py` | Organización del flujo de ejecución y menú | Integré el menú con validación de entradas y manejo explícito de errores sin romper el demo original. |

Para identificar la intervención de la IA en el código fuente utilicé comentarios explícitos:

```python
# [IA-Generated] SQL parametrizado para evitar inyección.
```

```python
# [IA-Refactored] Rechaza entradas malformadas antes de enviarlas.
```

Estas marcas permiten distinguir los bloques que recibieron asistencia y los que posteriormente fueron revisados o modificados por mí.

## 3. Evaluación Crítica y Análisis de Vulnerabilidades / Inconsistencias

No acepté automáticamente las primeras sugerencias de la IA. Revisé cada propuesta teniendo en cuenta tres criterios técnicos principales:

| Criterio | Decisión aplicada |
|---|---|
| **Seguridad** | No incluí tokens, contraseñas ni rutas sensibles directamente en el código. Validé las entradas HTTP y utilicé consultas SQL parametrizadas. |
| **Eficiencia** | Reutilicé la conexión SQLite y la sesión HTTP cuando corresponde, apliqué timeout en las solicitudes y agrupé las operaciones de escritura dentro de transacciones. |
| **Coherencia de dominio** | Conservé las clases y relaciones ya definidas. Los repositorios convierten filas de la base de datos en objetos del dominio, en lugar de mezclar SQL dentro de las entidades. |

Durante la revisión identifiqué estos riesgos o inconsistencias potenciales en las sugerencias iniciales:

- Una llamada HTTP directa sin sanitización podía aceptar cadenas con caracteres de control, entradas excesivamente largas o datos malformados.
- Construir consultas SQL concatenando valores recibidos desde el programa podía permitir inyección SQL.
- Guardar tokens o rutas concretas dentro del código dificultaría cambiar de entorno y podría exponer información sensible.
- Un error de red o de base de datos podía terminar el programa si no se traducía y manejaba de forma explícita.
- Crear conexiones o sesiones repetidamente podía desperdiciar recursos y hacer más difícil liberar correctamente los objetos.
- Algunas estructuras genéricas no conocían las relaciones entre empleados, proyectos y registros de tiempo, por lo que tuve que adaptarlas al modelo real.

Para comprobar las decisiones ejecuté la suite de pruebas del proyecto. La validación final fue:

```text
Ran 7 tests in 0.003s
OK
```

## 4. Refactorización y Modificaciones Aplicadas (Caso a Caso)

### Caso 1: Seguridad y Sanitización

Una propuesta inicial podía consultar la API directamente con el texto recibido del usuario. Consideré que ese enfoque era insuficiente porque no comprobaba el tipo, la longitud ni los caracteres permitidos.

Refactoricé el método `_sanitize_query` en `api_client.py` para validar y normalizar la entrada antes de enviarla:

```python
@staticmethod
def _sanitize_query(query: str) -> str:
    if not isinstance(query, str):
        raise TypeError("query debe ser texto")

    safe_query = query.strip()
    if not safe_query or len(safe_query) > 100:
        raise ValueError("query debe tener entre 1 y 100 caracteres")

    if re.search(r"[\x00-\x1f\x7f]", safe_query):
        raise ValueError("query contiene caracteres no permitidos")

    return safe_query
```

Con esta modificación rechazo caracteres de control, elimino espacios innecesarios y limito la longitud de la consulta. Además, el cliente utiliza timeout, valida la respuesta JSON y convierte los errores HTTP y de conexión en excepciones controladas.

### Caso 2: Persistencia y Sanitización SQL

En `repositories.py` aseguré que los valores no se incorporaran mediante concatenación de cadenas. Todas las operaciones CRUD utilizan parámetros de SQLite mediante `?`:

```python
connection.execute(
    "UPDATE empleados SET nombre = ?, email = ?, salario = ? "
    "WHERE id = ?",
    (nombre, email, str(salario), identificador),
)
```

Esta decisión reduce el riesgo de inyección SQL y separa los datos de la instrucción SQL. También mantuve la conversión explícita entre tipos Python y tipos almacenados: por ejemplo, las fechas se serializan con `isoformat()` y los valores monetarios se guardan como texto para reconstruirlos con `Decimal` sin depender de aproximaciones de `float`.

La clase `Database` activa las claves foráneas y ofrece un contexto transaccional. Cuando una operación SQLite falla, se ejecuta `rollback` y se lanza `PersistenceError`, evitando dejar cambios parciales.

### Caso 3: Manejo de Credenciales

Descarté cualquier sugerencia que implicara hardcodear tokens, contraseñas o rutas dependientes de una máquina. En `api_client.py` el token se obtiene desde una variable de entorno:

```python
self._token = token if token is not None else os.getenv("EXTERNAL_API_TOKEN")
```

La URL base también puede configurarse mediante `EXTERNAL_API_BASE_URL`. En `database.py`, la ruta de persistencia se puede cambiar mediante `PROJECT_DB_PATH`:

```python
configured_path = database_path or os.getenv("PROJECT_DB_PATH")
```

Así puedo separar la configuración del código fuente y utilizar valores distintos en desarrollo, pruebas y producción. El token tampoco se incluye en los mensajes de error ni en los logs.

### Manejo de errores y continuidad

En `main.py` integré un menú que valida las opciones del usuario y permite continuar después de errores controlados. Distingo entre fallos de red, errores de API, errores de SQLite, errores de persistencia y datos inconsistentes:

```python
try:
    action()
except requests.exceptions.RequestException:
    print("No se pudo completar la solicitud de red.")
except sqlite3.Error:
    print("No se pudo completar la operacion de base de datos.")
except PersistenceError as error:
    print(f"Error controlado de persistencia: {error}")
except (TypeError, ValueError) as error:
    print(f"Datos inconsistentes: {error}")
```

De esta manera, una entrada inválida o un problema externo no interrumpe innecesariamente toda la ejecución.

## 5. Conclusión y Justificación Técnica

La IA fue para mí un complemento de productividad. Me ayudó a obtener propuestas iniciales, comparar soluciones y detectar aspectos que debía revisar, pero no delegué en ella la responsabilidad técnica del proyecto.

La decisión final sobre seguridad, validación, manejo de excepciones, eficiencia y estructura fue guiada por mi análisis del problema y por los requisitos de la rúbrica. Conservé la separación de capas: los modelos representan el dominio, `repositories.py` maneja la persistencia, `database.py` administra SQLite, `api_client.py` encapsula la comunicación HTTP y `main.py` coordina la interacción con el usuario.

También verifiqué el resultado mediante pruebas automatizadas y ejecuciones del programa. Por eso considero que el código integrado no es únicamente una respuesta generada por IA, sino una solución revisada, refactorizada y adaptada al diseño orientado a objetos del proyecto.
