from decimal import Decimal
from typing import Protocol
from src.domain.models import Sesion, EstadoSesion


class PagoGateway(Protocol):
    def transferir(self, tutor_id: str, monto: Decimal) -> bool:
        ...


class SesionRepository(Protocol):
    def obtener_por_id(self, sesion_id: str) -> Sesion:
        ...

    def guardar(self, sesion: Sesion) -> None:
        ...


class LiquidacionService:
    def __init__(self, sesion_repo: SesionRepository, pago_gateway: PagoGateway):
        self.sesion_repo = sesion_repo
        self.pago_gateway = pago_gateway

    def procesar_liquidacion(self, sesion_id: str, grabacion_url: str, duracion_minutos: int) -> dict:
        sesion = self.sesion_repo.obtener_por_id(sesion_id)

        try:
            sesion.completar_con_grabacion(grabacion_url, duracion_minutos)
            self.sesion_repo.guardar(sesion)

            # Si la sesión quedó completada, se realiza la dispersión de fondos
            pago_exitoso = self.pago_gateway.transferir(sesion.tutor_id, sesion.liquidacion.monto_tutor)
            return {
                "sesion_id": sesion.id,
                "estado": sesion.estado.value,
                "pago_tutor": float(sesion.liquidacion.monto_tutor),
                "comision": float(sesion.liquidacion.comision),
                "transferencia_completada": pago_exitoso,
            }
        except Exception:
            self.sesion_repo.guardar(sesion)
            return {
                "sesion_id": sesion.id,
                "estado": sesion.estado.value,
                "pago_tutor": 0.0,
                "comision": 0.0,
                "transferencia_completada": False,
                "mensaje": "No aplicable - reembolso",
            }