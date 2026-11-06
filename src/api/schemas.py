from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.domain.models import Modalidad


class ReservaRequest(BaseModel):
    sesion_id: str = Field(..., example="SES-101")
    estudiante_id: str = Field(..., example="EST-01")
    tutor_id: str = Field(..., example="TUT-05")
    materia: str = Field(..., example="Cálculo Diferencial")
    tema: str = Field(..., example="Derivadas")
    modalidad: Modalidad = Field(..., example=Modalidad.EN_LINEA)
    fecha_hora_programada: datetime = Field(..., example="2026-11-20T10:00:00")


class ReservaResponse(BaseModel):
    id: str
    estudiante_id: str
    tutor_id: str
    materia: str
    estado: str
    precio: float
    fecha_hora_programada: datetime


class LiquidacionRequest(BaseModel):
    grabacion_url: str = Field(..., example="https://aulaplus.com/evidencias/grabacion101.mp4")
    duracion_minutos: int = Field(..., example=90)


class LiquidacionResponse(BaseModel):
    sesion_id: str
    estado: str
    pago_tutor: float
    comision: float
    transferencia_completada: bool
    mensaje: Optional[str] = None