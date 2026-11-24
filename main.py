import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-for-dev")

app = FastAPI(title="Sistema de Encuestas - Reto 0")

# Bases de datos en memoria para la aplicación
usuarios_db = {}  # username -> {id, username, password, role}
encuestas_db = {}  # id -> {id, titulo, creador_id, opciones: [{id, texto, votos}]}
sesiones_db = {}  # token -> username

class RegistroUsuario(BaseModel):
    username: str
    password: str

class CrearEncuesta(BaseModel):
    titulo: str
    opciones: list[str]

class VotarEncuesta(BaseModel):
    opcion_id: int

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
    # FALLO 1: Contraseñas sin hash (se guarda en texto plano)
    nuevo_id = len(usuarios_db) + 1
    usuario = {
        "id": nuevo_id,
        "username": datos.username,
        "password": datos.password  # Texto plano
    }
    usuarios_db[datos.username] = usuario
    return {"id": nuevo_id, "username": datos.username}

@app.post("/api/login")
def login(datos: RegistroUsuario):
    usuario = usuarios_db.get(datos.username)
    if not usuario or usuario["password"] != datos.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = f"token-{datos.username}"
    sesiones_db[token] = datos.username
    return {"token": token, "username": datos.username}

@app.post("/api/encuestas")
def crear_encuesta(datos: CrearEncuesta, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # FALLO 3: Validación de entradas ausente (permite títulos vacíos)
    nueva_id = len(encuestas_db) + 1
    encuesta = {
        "id": nueva_id,
        "titulo": datos.titulo,
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
    
    # FALLO 2: Control de acceso roto (cualquiera puede borrarla sin verificar creador_id)
    del encuestas_db[encuesta_id]
    return {"detail": "Encuesta eliminada exitosamente"}
