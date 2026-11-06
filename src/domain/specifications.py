from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.domain.models import Grabacion


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool:
        pass

    def __and__(self, other: "Specification") -> "Specification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "Specification":
        return OrSpecification(self, other)

    def __invert__(self) -> "Specification":
        return NotSpecification(self)


class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, candidate) -> bool:
        return not self.spec.is_satisfied_by(candidate)


@dataclass
class SolicitudReservaContext:
    fecha_programada: datetime
    fecha_actual: datetime
    sesiones_tutor_ese_dia: int


# Especificación 1: Anticipación mínima de 48 horas (US-01 / CP-01, CP-02, CP-03)
class AnticipacionMinimaSpec(Specification):
    def is_satisfied_by(self, candidate: SolicitudReservaContext) -> bool:
        return candidate.fecha_programada >= (candidate.fecha_actual + timedelta(hours=48))


# Especificación 2: Límite de máximo 5 sesiones diarias por tutor (US-10 / CP-10, CP-11)
class LimiteDiarioTutorSpec(Specification):
    def is_satisfied_by(self, candidate: SolicitudReservaContext) -> bool:
        return candidate.sesiones_tutor_ese_dia < 5


# Especificación 3: Duración mínima de grabación >= 70% (US-14 / CP-04 a CP-07)
class GrabacionAprobadaSpec(Specification):
    def is_satisfied_by(self, candidate: Grabacion) -> bool:
        return candidate.es_duracion_valida()