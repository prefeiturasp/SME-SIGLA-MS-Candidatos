# Models module for candidatos app
from .base import BaseModel
from .candidato import Candidato
from .concurso_candidato import ConcursoCandidato
from .lote import ConcursoCandidatosLote
from .parametrizacao import Parametrizacao

__all__ = [
    'BaseModel',
    'Candidato',
    'ConcursoCandidato',
    'ConcursoCandidatosLote',
    'Parametrizacao',
]
