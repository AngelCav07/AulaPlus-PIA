from typing import Optional
from sqlalchemy.orm import Session
from src.domain.models import Sesion, EstadoSesion, Modalidad, Grabacion
from src.infrastructure.database import SesionModel


class SqlAlchemySesionRepository:
    def __init__(self, db: Session):
        self.db = db

    def guardar(self, sesion: Sesion) -> None:
        model = self.db.query(SesionModel).filter(SesionModel.id == sesion.id).first()
        if not model:
            model = SesionModel(
                id=sesion.id,
                estudiante_id=sesion.estudiante_id,
                tutor_id=sesion.tutor_id,
                materia=sesion.materia,
                tema=sesion.tema,
                modalidad=sesion.modalidad.value,
                fecha_hora_programada=sesion.fecha_hora_programada,
                estado=sesion.estado.value,
                precio=float(sesion.liquidacion.precio),
                comision=float(sesion.liquidacion.comision),
                monto_tutor=float(sesion.liquidacion.monto_tutor),
            )
            self.db.add(model)
        else:
            model.estado = sesion.estado.value
            if sesion.grabacion:
                model.grabacion_url = sesion.grabacion.url
                model.grabacion_duracion = sesion.grabacion.duracion_minutos

    def obtener_por_id(self, sesion_id: str) -> Optional[Sesion]:
        model = self.db.query(SesionModel).filter(SesionModel.id == sesion_id).first()
        if not model:
            return None

        sesion = Sesion(
            sesion_id=model.id,
            estudiante_id=model.estudiante_id,
            tutor_id=model.tutor_id,
            materia=model.materia,
            tema=model.tema,
            modalidad=Modalidad(model.modalidad),
            fecha_hora_programada=model.fecha_hora_programada,
            estado=EstadoSesion(model.estado),
        )

        if model.grabacion_url and model.grabacion_duracion:
            sesion.grabacion = Grabacion(
                url=model.grabacion_url,
                duracion_minutos=model.grabacion_duracion,
            )

        return sesion