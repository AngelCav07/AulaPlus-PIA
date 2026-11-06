from decimal import Decimal


class MockPagoGateway:
    """Adaptador de pasarela externa simulada para liquidaciones."""
    def transferir(self, tutor_id: str, monto: Decimal) -> bool:
        # En entorno de producción se conectaría con Stripe / Openpay / SPEI
        return True