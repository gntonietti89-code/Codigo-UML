# Modelo UML en Python

Implementacion orientada a objetos del dominio de usuarios, departamentos,
proyectos y registros de tiempo.

## Ejecutar una comprobacion rapida

Desde esta carpeta:

```bash
python -m unittest discover -s tests -v
```

La implementacion usa `datetime.date` para fechas y `decimal.Decimal` para
salarios, presupuestos, horas y tarifas. Las colecciones se exponen como
tuplas o `frozenset` para evitar modificaciones externas no controladas.

## Persistencia

La capa SQLite se encuentra en `database.py` y crea por defecto
`data/gestion.db`. Se puede cambiar la ruta sin modificar el codigo:

```powershell
$env:PROJECT_DB_PATH = "C:\\datos\\gestion.db"
```

El esquema se inicializa con `Database.initialize_schema()` y los repositorios
de `repositories.py` ofrecen `create`, `get`, `list`, `update` y `delete`.
Las consultas usan parametros, las transacciones hacen `commit`/`rollback` y
las claves foraneas estan activadas.

## Cliente API

Instalar dependencias y configurar la API:

```bash
python -m pip install -r requirements.txt
```

```powershell
$env:EXTERNAL_API_BASE_URL = "https://api.example.com"
$env:EXTERNAL_API_TOKEN = "token-local-no-versionado"
```

`api_client.py` no contiene tokens, valida entradas, usa timeout, procesa JSON
y convierte errores HTTP, de timeout y de conectividad a excepciones propias.
Los tests inyectan una sesion HTTP simulada, por lo que no requieren secretos
ni acceso a internet.