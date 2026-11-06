from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from src.infrastructure.database import Base, get_engine, get_session_factory
from src.infrastructure.repository import SqlAlchemySesionRepository
from src.infrastructure.adapters import MockPagoGateway
from src.application.services import LiquidacionService
from src.domain.models import Sesion
from src.domain.exceptions import (
    AnticipacionInsuficienteException,
    DuracionInsuficienteException,
    TransicionInvalidaException,
)
from src.api.schemas import (
    ReservaRequest,
    ReservaResponse,
    LiquidacionRequest,
    LiquidacionResponse,
)

# Inicializar motor y tablas SQLite
engine = get_engine()
Base.metadata.create_all(bind=engine)
SessionFactory = get_session_factory(engine)

app = FastAPI(
    title="AulaPlus API",
    description="API REST de Lógica de Negocio para el sistema AulaPlus",
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "servicio": "AulaPlus Core API"}


@app.post(
    "/sesiones/reservar",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Sesiones"],
)
def reservar_sesion(request: ReservaRequest):
    db = SessionFactory()
    repo = SqlAlchemySesionRepository(db)
    ahora = datetime.now()

    try:
        sesion = Sesion.crear(
            sesion_id=request.sesion_id,
            estudiante_id=request.estudiante_id,
            tutor_id=request.tutor_id,
            materia=request.materia,
            tema=request.tema,
            modalidad=request.modalidad,
            fecha_hora_programada=request.fecha_hora_programada,
            fecha_actual=ahora,
        )
        repo.guardar(sesion)
        db.commit()

        return ReservaResponse(
            id=sesion.id,
            estudiante_id=sesion.estudiante_id,
            tutor_id=sesion.tutor_id,
            materia=sesion.materia,
            estado=sesion.estado.value,
            precio=float(sesion.liquidacion.precio),
            fecha_hora_programada=sesion.fecha_hora_programada,
        )
    except AnticipacionInsuficienteException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()


@app.post(
    "/sesiones/{sesion_id}/liquidar",
    response_model=LiquidacionResponse,
    tags=["Liquidaciones"],
)
def liquidar_sesion(sesion_id: str, request: LiquidacionRequest):
    db = SessionFactory()
    repo = SqlAlchemySesionRepository(db)
    gateway = MockPagoGateway()
    servicio = LiquidacionService(repo, gateway)

    sesion_existente = repo.obtener_por_id(sesion_id)
    if not sesion_existente:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesión {sesion_id} no encontrada",
        )

    try:
        resultado = servicio.procesar_liquidacion(
            sesion_id=sesion_id,
            grabacion_url=request.grabacion_url,
            duracion_minutos=request.duracion_minutos,
        )
        db.commit()
        return LiquidacionResponse(**resultado)
    except TransicionInvalidaException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    finally:
        db.close()