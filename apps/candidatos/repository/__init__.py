"""Repositórios de acesso a dados do app candidatos."""

from .candidato_repository import CandidatoRepository
from .concurso_candidato_eliminacao_repository import (
    ConcursoCandidatoEliminacaoRepository,
)
from .concurso_candidato_historico_classificacao_repository import (
    ConcursoCandidatoHistoricoClassificacaoRepository,
)
from .concurso_candidato_reclassificacao_repository import (
    ConcursoCandidatoReclassificacaoRepository,
)
from .concurso_candidato_repository import ConcursoCandidatoRepository

__all__ = [
    "CandidatoRepository",
    "ConcursoCandidatoRepository",
    "ConcursoCandidatoReclassificacaoRepository",
    "ConcursoCandidatoEliminacaoRepository",
    "ConcursoCandidatoHistoricoClassificacaoRepository",
]
