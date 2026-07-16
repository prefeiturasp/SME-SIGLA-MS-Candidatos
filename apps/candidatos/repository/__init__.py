"""Repositórios de acesso a dados do app candidatos."""

from .candidato_repository import CandidatoRepository
from .concurso_candidato_eliminacao_repository import (
    ConcursoCandidatoEliminacaoRepository,
)
from .concurso_candidato_reclassificacao_repository import (
    ConcursoCandidatoReclassificacaoRepository,
)
from .concurso_candidato_repository import ConcursoCandidatoRepository
from .concurso_candidatos_lote_repository import (
    ConcursoCandidatosLoteRepository,
)

__all__ = [
    "CandidatoRepository",
    "ConcursoCandidatosLoteRepository",
    "ConcursoCandidatoRepository",
    "ConcursoCandidatoReclassificacaoRepository",
    "ConcursoCandidatoEliminacaoRepository",
]
