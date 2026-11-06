from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class SesionModel(Base):
    __tablename__ = "sesiones"

    id = Column(String, primary_key=True)
    estudiante_id = Column(String, nullable=False)
    tutor_id = Column(String, nullable=False)
    materia = Column(String, nullable=False)
    tema = Column(String, nullable=False)
    modalidad = Column(String, nullable=False)
    fecha_hora_programada = Column(DateTime, nullable=False)
    estado = Column(String, nullable=False)
    precio = Column(Float, default=200.0)
    comision = Column(Float, default=40.0)
    monto_tutor = Column(Float, default=160.0)
    grabacion_url = Column(String, nullable=True)
    grabacion_duracion = Column(Integer, nullable=True)


def get_engine(db_url: str = "sqlite:///./aulaplus.db"):
    return create_engine(db_url, connect_args={"check_same_thread": False})


def get_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)