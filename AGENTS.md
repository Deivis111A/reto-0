# AGENTS.md

## Proyecto
Plataforma de Encuestas en línea para crear, responder y consultar votaciones.
Módulo de reto 0 desarrollado en FastAPI con autenticación y almacenamiento en memoria.

## Stack
- Python 3.14, FastAPI, Jinja2, Uvicorn
- pytest con TestClient, Ruff y pre-commit

## Comandos
- Instalar: `pip install -r requirements.txt`
- Ejecutar: `uvicorn main:app --reload`
- Pruebas: `python -m pytest -v`
- Estilo: `ruff check .`

## Estructura
- `main.py`: aplicación FastAPI, rutas, autenticación y lógica de encuestas
- `tests/test_humo.py`: prueba de verificación de arranque y respuesta HTTP 200
- `tests/test_fallos.py`: pruebas de demostración y regresión de los tres fallos

## Qué no hacer
- No modificar las pruebas para que pasen: se corrige el código de la aplicación.
- No escribir contraseñas ni claves secretas en el código: usar variables de entorno.
- No instalar dependencias sin explicar para qué y verificar que existen en pypi.org.
- No hacer commit ni push: los realiza el desarrollador.

## Lecciones aprendidas
- Las contraseñas se guardan siempre con hash criptográfico, nunca en texto plano.
- En endpoints de modificación o eliminación, siempre verificar que el registro pertenezca al usuario de la sesión.
- Validar siempre en el servidor los campos obligatorios, longitud y contenido antes de almacenar datos.
