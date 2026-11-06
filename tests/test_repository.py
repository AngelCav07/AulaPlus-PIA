from datetime import datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models import Sesion, Modalidad
from src.infrastructure.database import Base
from src.infrastructure.repository import SqlAlchemySesionRepository


@pytest.fixture
def db_session():
    # Base de datos aislada en memoria para pruebas
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


# CP-12: Guardar sesión con commit persiste; con rollback no existe
def test_cp12_commit_persiste_la_sesion(db_session):
    repo = SqlAlchemySesionRepository(db_session)
    ahora = datetime(2026, 11, 10, 10, 0, 0)
    sesion = Sesion.crear(
        "SES-REPO-01", "EST-01", "TUT-01", "Física", "Termodinámica",
        Modalidad.EN_LINEA, ahora + timedelta(hours=48), ahora
    )

    repo.guardar(sesion)
    db_session.commit()

    recuperada = repo.obtener_por_id("SES-REPO-01")
    assert recuperada is not None
    assert recuperada.materia == "Física"


def test_cp12_rollback_descarta_la_sesion(db_session):
    repo = SqlAlchemySesionRepository(db_session)
    ahora = datetime(2026, 11, 10, 10, 0, 0)
    sesion = Sesion.crear(
        "SES-REPO-02", "EST-01", "TUT-01", "Química", "Orgánica",
        Modalidad.EN_LINEA, ahora + timedelta(hours=48), ahora
    )

    repo.guardar(sesion)
    db_session.rollback()

    recuperada = repo.obtener_por_id("SES-REPO-02")
    assert recuperada is None