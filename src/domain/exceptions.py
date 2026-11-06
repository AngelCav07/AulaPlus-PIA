class ReglaNegocioException(Exception):
    pass


class AnticipacionInsuficienteException(ReglaNegocioException):
    pass


class DuracionInsuficienteException(ReglaNegocioException):
    pass


class TransicionInvalidaException(ReglaNegocioException):
    pass