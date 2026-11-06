from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_reservar_sesion_exitosa():
    fecha_valida = (datetime.now() + timedelta(hours=72)).isoformat()
    payload = {
        "sesion_id": "SES-API-01",
        "estudiante_id": "EST-01",
        "tutor_id": "TUT-02",
        "materia": "Física",
        "tema": "Cinemática",
        "modalidad": "EnLinea",
        "fecha_hora_programada": fecha_valida,
    }

    response = client.post("/sesiones/reservar", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "SES-API-01"
    assert data["estado"] == "Confirmada"
    assert data["precio"] == 200.0


def test_api_reservar_sesion_con_menos_de_48_horas_falla():
    fecha_invalida = (datetime.now() + timedelta(hours=10)).isoformat()
    payload = {
        "sesion_id": "SES-API-02",
        "estudiante_id": "EST-01",
        "tutor_id": "TUT-02",
        "materia": "Física",
        "tema": "Cinemática",
        "modalidad": "Presencial",
        "fecha_hora_programada": fecha_invalida,
    }

    response = client.post("/sesiones/reservar", json=payload)
    assert response.status_code == 400
    assert "al menos 48 horas" in response.json()["detail"]


def test_api_liquidar_sesion_completada():
    # 1. Crear sesión válida
    fecha = (datetime.now() + timedelta(hours=50)).isoformat()
    client.post("/sesiones/reservar", json={
        "sesion_id": "SES-API-03",
        "estudiante_id": "EST-05",
        "tutor_id": "TUT-01",
        "materia": "Programación",
        "tema": "FastAPI",
        "modalidad": "EnLinea",
        "fecha_hora_programada": fecha,
    })

    # 2. Liquidar con 90 minutos de grabación
    liq_payload = {
        "grabacion_url": "https://aulaplus.com/rec3.mp4",
        "duracion_minutos": 90,
    }
    response = client.post("/sesiones/SES-API-03/liquidar", json=liq_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "Completada"
    assert data["pago_tutor"] == 160.0
    assert data["transferencia_completada"] is True


def test_api_liquidar_sesion_inexistente_retorna_404():
    response = client.post("/sesiones/NO-EXISTE/liquidar", json={
        "grabacion_url": "https://aulaplus.com/nada.mp4",
        "duracion_minutos": 90,
    })
    assert response.status_code == 404