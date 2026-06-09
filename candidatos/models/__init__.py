# Models module for candidatos app
"""Módulo models/__init__."""

from .base import BaseModel
from .candidato import Candidato
from .concurso_candidato import ConcursoCandidato
from .eliminacao import ConcursoCandidatoEliminacao
from .lote import ConcursoCandidatosLote
from .parametrizacao import Parametrizacao
from .reclassificacao import ConcursoCandidatoReclassificacao

__all__ = [
    "BaseModel",
    "Candidato",
    "ConcursoCandidato",
    "ConcursoCandidatosLote",
    "Parametrizacao",
    "ConcursoCandidatoReclassificacao",
    "ConcursoCandidatoEliminacao",
]
