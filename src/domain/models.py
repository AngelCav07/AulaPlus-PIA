from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class EstadoSesion(str, Enum):
    PROGRAMADA = "Programada"
    CONFIRMADA = "Confirmada"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    REEMBOLSADA = "Reembolsada"


class Modalidad(str, Enum):
    PRESENCIAL = "Presencial"
    EN_LINEA = "EnLinea"


@dataclass(frozen=True)
class Liquidacion:
    precio: Decimal = Decimal("200.00")
    comision: Decimal = Decimal("40.00")
    monto_tutor: Decimal = Decimal("160.00")


@dataclass(frozen=True)
class Grabacion:
    url: str
    duracion_minutos: int
    minutos_totales: int = 90
    umbral_minimo: float = 0.70

    def es_duracion_valida(self) -> bool:
        # 70% de 90 minutos son exactamente 63 minutos
        return self.duracion_minutos >= (self.minutos_totales * self.umbral_minimo)


class Sesion:
    def __init__(
        self,
        sesion_id: str,
        estudiante_id: str,
        tutor_id: str,
        materia: str,
        tema: str,
        modalidad: Modalidad,
        fecha_hora_programada: datetime,
        estado: EstadoSesion = EstadoSesion.CONFIRMADA,
    ):
        self.id = sesion_id
        self.estudiante_id = estudiante_id
        self.tutor_id = tutor_id
        self.materia = materia
        self.tema = tema
        self.modalidad = modalidad
        self.fecha_hora_programada = fecha_hora_programada
        self.estado = estado
        self.liquidacion = Liquidacion()
        self.grabacion: Optional[Grabacion] = None

    @classmethod
    def crear(
        cls,
        sesion_id: str,
        estudiante_id: str,
        tutor_id: str,
        materia: str,
        tema: str,
        modalidad: Modalidad,
        fecha_hora_programada: datetime,
        fecha_actual: datetime,
    ) -> "Sesion":
        from src.domain.exceptions import AnticipacionInsuficienteException

        # Regla: Anticipación mínima de 48 horas (CP-01, CP-02, CP-03)
        if fecha_hora_programada < (fecha_actual + timedelta(hours=48)):
            raise AnticipacionInsuficienteException(
                "La reserva debe realizarse con al menos 48 horas de anticipación"
            )

        return cls(
            sesion_id=sesion_id,
            estudiante_id=estudiante_id,
            tutor_id=tutor_id,
            materia=materia,
            tema=tema,
            modalidad=modalidad,
            fecha_hora_programada=fecha_hora_programada,
            estado=EstadoSesion.CONFIRMADA,
        )

    def completar_con_grabacion(self, url: str, duracion_minutos: int) -> None:
        from src.domain.exceptions import DuracionInsuficienteException, TransicionInvalidaException

        if self.estado != EstadoSesion.CONFIRMADA:
            raise TransicionInvalidaException("Solo se pueden completar sesiones confirmadas.")

        self.grabacion = Grabacion(url=url, duracion_minutos=duracion_minutos)

        # Regla: Si dura >= 70% se completa; si dura < 70% se reembolsa (CP-04 a CP-07)
        if self.grabacion.es_duracion_valida():
            self.estado = EstadoSesion.COMPLETADA
        else:
            self.estado = EstadoSesion.REEMBOLSADA
            raise DuracionInsuficienteException("La duración de la grabación es menor al 70% del tiempo pactado")

    def cancelar_por_soporte(self) -> None:
        from src.domain.exceptions import TransicionInvalidaException

        if self.estado in (EstadoSesion.COMPLETADA, EstadoSesion.CANCELADA):
            raise TransicionInvalidaException("No se puede cancelar una sesión finalizada o previamente cancelada.")

        self.estado = EstadoSesion.CANCELADA