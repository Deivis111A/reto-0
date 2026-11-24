import hashlib
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-for-dev")

app = FastAPI(title="Sistema de Encuestas - Reto 0")

usuarios_db = {}
encuestas_db = {}
sesiones_db = {}

def hashear_password(password: str) -> str:
    """Aplica hash seguro SHA-256 a la contraseña."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class RegistroUsuario(BaseModel):
    username: str
    password: str

class CrearEncuesta(BaseModel):
    titulo: str
    opciones: list[str]

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header not in sesiones_db:
        return None
    username = sesiones_db[auth_header]
    return usuarios_db.get(username)

@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html><html><head><title>Encuestas</title></head><body><h1>Sistema de Encuestas</h1></body></html>"""

@app.post("/api/registro")
def registrar(datos: RegistroUsuario):
    if datos.username in usuarios_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    if len(datos.password.strip()) < 6:
        raise HTTPException(status_code=422, detail="La contraseña debe tener al menos 6 caracteres")
    
    # CORRECCIÓN 1: Aplicación de hash seguro a la contraseña
    nuevo_id = len(usuarios_db) + 1
    usuario = {
        "id": nuevo_id,
        "username": datos.username,
        "password": hashear_password(datos.password)
    }
    usuarios_db[datos.username] = usuario
    return {"id": nuevo_id, "username": datos.username}

@app.post("/api/login")
def login(datos: RegistroUsuario):
    usuario = usuarios_db.get(datos.username)
    # Verificación comparando hashes
    if not usuario or usuario["password"] != hashear_password(datos.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = f"token-{datos.username}"
    sesiones_db[token] = datos.username
    return {"token": token, "username": datos.username}

@app.post("/api/encuestas")
def crear_encuesta(datos: CrearEncuesta, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # CORRECCIÓN 3: Validación estricta de título y opciones
    titulo_limpio = datos.titulo.strip()
    if not titulo_limpio or len(titulo_limpio) > 120:
        raise HTTPException(status_code=422, detail="El título es obligatorio y máximo 120 caracteres")
    if not datos.opciones or len(datos.opciones) < 2:
        raise HTTPException(status_code=422, detail="La encuesta debe tener al menos 2 opciones")
    
    nueva_id = len(encuestas_db) + 1
    encuesta = {
        "id": nueva_id,
        "titulo": titulo_limpio,
        "creador_id": user["id"],
        "opciones": [{"id": i, "texto": opt, "votos": 0} for i, opt in enumerate(datos.opciones)]
    }
    encuestas_db[nueva_id] = encuesta
    return encuesta

@app.get("/api/encuestas")
def listar_encuestas():
    return list(encuestas_db.values())

@app.delete("/api/encuestas/{encuesta_id}")
def eliminar_encuesta(encuesta_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    encuesta = encuestas_db.get(encuesta_id)
    if not encuesta:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    
    # CORRECCIÓN 2: Validación de control de acceso por propietario
    if encuesta["creador_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta encuesta")
    
    del encuestas_db[encuesta_id]
    return {"detail": "Encuesta eliminada exitosamente"}
