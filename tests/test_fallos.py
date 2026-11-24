import random
import hashlib
from fastapi.testclient import TestClient
from main import app, usuarios_db, encuestas_db

cliente = TestClient(app)

def test_contrasena_guardada_con_hash():
    """Fallo 1: Las contraseñas deben almacenarse usando una función de hash criptográfica."""
    rnd = random.randint(1000, 9999)
    usuario = f"usuario_test_{rnd}"
    clave_plana = "Clave123*"
    
    resp = cliente.post("/api/registro", json={"username": usuario, "password": clave_plana})
    assert resp.status_code == 200
    
    # La contraseña en base de datos NO debe ser la clave plana
    guardada = usuarios_db[usuario]["password"]
    assert guardada != clave_plana
    # Debe ser un hash sha256 de 64 caracteres
    assert len(guardada) == 64

def test_control_acceso_eliminar_encuesta_ajena():
    """Fallo 2: Un usuario no puede eliminar encuestas creadas por otro usuario."""
    # Registrar usuario A y crear encuesta
    rnd = random.randint(1000, 9999)
    u_a = f"creador_{rnd}"
    u_b = f"intruso_{rnd}"
    cliente.post("/api/registro", json={"username": u_a, "password": "Password123*"})
    cliente.post("/api/registro", json={"username": u_b, "password": "Password123*"})
    
    token_a = cliente.post("/api/login", json={"username": u_a, "password": "Password123*"}).json()["token"]
    token_b = cliente.post("/api/login", json={"username": u_b, "password": "Password123*"}).json()["token"]
    
    encuesta = cliente.post(
        "/api/encuestas",
        headers={"Authorization": token_a},
        json={"titulo": "Encuesta Clave", "opciones": ["Si", "No"]}
    ).json()
    encuesta_id = encuesta["id"]
    
    # Usuario B intenta eliminar la encuesta del Usuario A
    resp_b = cliente.delete(f"/api/encuestas/{encuesta_id}", headers={"Authorization": token_b})
    assert resp_b.status_code == 403
    assert encuesta_id in encuestas_db

def test_validacion_titulo_encuesta_no_vacio():
    """Fallo 3: No se deben permitir encuestas con título vacío o sólo espacios."""
    rnd = random.randint(1000, 9999)
    user = f"autor_{rnd}"
    cliente.post("/api/registro", json={"username": user, "password": "Password123*"})
    token = cliente.post("/api/login", json={"username": user, "password": "Password123*"}).json()["token"]
    
    resp_vacio = cliente.post(
        "/api/encuestas",
        headers={"Authorization": token},
        json={"titulo": "   ", "opciones": ["A", "B"]}
    )
    assert resp_vacio.status_code in [400, 422]
