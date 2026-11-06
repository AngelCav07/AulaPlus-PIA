from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock
import pytest

from src.domain.models import Sesion, EstadoSesion, Modalidad, Grabacion
from src.domain.exceptions import AnticipacionInsuficienteException, DuracionInsuficienteException
from src.domain.specifications import (
    AnticipacionMinimaSpec,
    LimiteDiarioTutorSpec,
    GrabacionAprobadaSpec,
    SolicitudReservaContext,
)
from src.application.services import LiquidacionService


@pytest.fixture
def fecha_base():
    return datetime(2026, 11, 10, 10, 0, 0)


# CP-01: Reserva con 72 h de anticipación -> Confirmada
def test_cp01_reserva_con_72_horas_queda_confirmada(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=72)
    sesion = Sesion.crear("SES-01", "EST-01", "TUT-01", "Matemáticas", "Álgebra", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    assert sesion.estado == EstadoSesion.CONFIRMADA
    assert sesion.liquidacion.precio == Decimal("200.00")
    assert sesion.liquidacion.comision == Decimal("40.00")
    assert sesion.liquidacion.monto_tutor == Decimal("160.00")


# CP-02: Reserva con 24 h de anticipación -> Excepción
def test_cp02_reserva_con_24_horas_es_rechazada(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=24)
    with pytest.raises(AnticipacionInsuficienteException) as exc_info:
        Sesion.crear("SES-02", "EST-01", "TUT-01", "Física", "Dinámica", Modalidad.PRESENCIAL, fecha_prog, fecha_base)

    assert "La reserva debe realizarse con al menos 48 horas de anticipación" in str(exc_info.value)


# CP-03: Reserva con exactamente 48 h -> Aceptada en el límite
def test_cp03_reserva_con_exactamente_48_horas_es_aceptada(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-03", "EST-01", "TUT-01", "Programación", "Lógica", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    assert sesion.estado == EstadoSesion.CONFIRMADA


# CP-04: Grabación de 90 min (100%) -> Completada
def test_cp04_sesion_de_90_minutos_se_completa(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-04", "EST-01", "TUT-01", "Cálculo", "Integrales", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    sesion.completar_con_grabacion("https://aulaplus.com/evidencia1.mp4", 90)

    assert sesion.estado == EstadoSesion.COMPLETADA
    assert sesion.grabacion.es_duracion_valida() is True


# CP-05: Grabación de 45 min (<70%) -> Reembolso
def test_cp05_sesion_de_45_minutos_es_rechazada_por_duracion(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-05", "EST-01", "TUT-01", "Cálculo", "Límites", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    with pytest.raises(DuracionInsuficienteException):
        sesion.completar_con_grabacion("https://aulaplus.com/evidencia2.mp4", 45)

    assert sesion.estado == EstadoSesion.REEMBOLSADA


# CP-06: Grabación de 63 min (70% exacto) -> Completada sin reembolso
def test_cp06_sesion_de_63_minutos_exactos_se_completa(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-06", "EST-01", "TUT-01", "Química", "Gases", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    sesion.completar_con_grabacion("https://aulaplus.com/evidencia3.mp4", 63)

    assert sesion.estado == EstadoSesion.COMPLETADA


# CP-07: Grabación de 62 min (<70%) -> Reembolso
def test_cp07_sesion_de_62_minutos_es_rechazada(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-07", "EST-01", "TUT-01", "Química", "Reacciones", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    with pytest.raises(DuracionInsuficienteException):
        sesion.completar_con_grabacion("https://aulaplus.com/evidencia4.mp4", 62)

    assert sesion.estado == EstadoSesion.REEMBOLSADA


# CP-08: Liquidación con pasarela de pago llamada con $160
def test_cp08_sesion_completa_transfiere_160_al_tutor(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-08", "EST-01", "TUT-01", "Física", "Óptica", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    repo_mock = Mock()
    repo_mock.obtener_por_id.return_value = sesion

    gateway_mock = Mock()
    gateway_mock.transferir.return_value = True

    servicio = LiquidacionService(repo_mock, gateway_mock)
    resultado = servicio.procesar_liquidacion("SES-08", "https://aulaplus.com/evidencia.mp4", 90)

    assert resultado["estado"] == "Completada"
    assert resultado["pago_tutor"] == 160.0
    gateway_mock.transferir.assert_called_once_with("TUT-01", Decimal("160.00"))


# CP-09: Liquidación con sesión reembolsada no transfiere
def test_cp09_sesion_con_reembolso_no_llama_a_pasarela(fecha_base):
    fecha_prog = fecha_base + timedelta(hours=48)
    sesion = Sesion.crear("SES-09", "EST-01", "TUT-01", "Física", "Calor", Modalidad.EN_LINEA, fecha_prog, fecha_base)

    repo_mock = Mock()
    repo_mock.obtener_por_id.return_value = sesion

    gateway_mock = Mock()

    servicio = LiquidacionService(repo_mock, gateway_mock)
    resultado = servicio.procesar_liquidacion("SES-09", "https://aulaplus.com/evidencia.mp4", 45)

    assert resultado["estado"] == "Reembolsada"
    assert resultado["mensaje"] == "No aplicable - reembolso"
    gateway_mock.transferir.assert_not_called()


# Pruebas de Patrón Specification combinadas (&, |, ~)
def test_specification_combinada_reserva_valida(fecha_base):
    contexto = SolicitudReservaContext(
        fecha_programada=fecha_base + timedelta(hours=50),
        fecha_actual=fecha_base,
        sesiones_tutor_ese_dia=3,
    )

    spec = AnticipacionMinimaSpec() & LimiteDiarioTutorSpec()
    assert spec.is_satisfied_by(contexto) is True


def test_specification_combinada_tutor_con_cinco_sesiones(fecha_base):
    contexto = SolicitudReservaContext(
        fecha_programada=fecha_base + timedelta(hours=50),
        fecha_actual=fecha_base,
        sesiones_tutor_ese_dia=5,  # Tutor al límite diario
    )

    spec = AnticipacionMinimaSpec() & LimiteDiarioTutorSpec()
    assert spec.is_satisfied_by(contexto) is False