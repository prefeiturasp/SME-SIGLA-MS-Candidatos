"""Módulo service/candidato_lote_service."""

from typing import Any

from candidatos.repository import ConcursoCandidatoRepository
from rest_framework import status

from .candidato_service import CandidatoService


class CandidatoLoteService:
    """Service para criação de candidatos em lote."""

    @staticmethod
    def _resolver_mandado_judicial(
        mandado_judicial: bool, concurso_uuid: Any
    ) -> bool:
        """Ajusta mandado_judicial conforme existência no concurso.

        Regras:
        - Se vier ``True`` e o concurso ainda não tiver candidatos → ``False``.
        - Se vier ``True`` e já houver candidatos → permanece ``True``.
        - Se vier ``False`` e já houver candidatos → vira ``True``.
        - Se vier ``False`` e não houver candidatos → permanece ``False``.

        Args:
            mandado_judicial: Valor enviado no payload.
            concurso_uuid: UUID do concurso.

        Returns:
            Valor efetivo de ``mandado_judicial`` após a checagem.
        """
        ja_existe = ConcursoCandidatoRepository.existe_por_concurso_uuid(
            concurso_uuid
        )
        if mandado_judicial:
            return bool(ja_existe)
        if ja_existe:
            return True
        return False

    @classmethod
    def processar_criacao_candidatos_lote(
        cls,
        data: dict[str, Any],
    ) -> tuple[dict[str, Any], int]:
        """Processa criacao candidatos lote.

        Args:
            data: Data.

        Returns:
            Tupla com os objetos criados ou atualizados.
        """
        concurso_uuid = data.get("concurso_uuid")
        if not concurso_uuid:
            return {
                "detail": "concurso_uuid é obrigatório"
            }, status.HTTP_400_BAD_REQUEST

        concurso_nome = data.get("concurso_nome", "")
        mandado_judicial = cls._resolver_mandado_judicial(
            bool(data.get("mandado_judicial", False)),
            concurso_uuid,
        )
        itens: list[dict[str, Any]] = []
        for item in data.get("candidatos", []):
            _cand, concurso = CandidatoService.upsert_candidato_e_concurso(
                item,
                concurso_uuid=concurso_uuid,
                concurso_nome=concurso_nome,
                mandado_judicial=mandado_judicial,
            )
            itens.append(
                {
                    "candidato_uuid": concurso.candidato_id,
                    "concurso_id": concurso.id,
                }
            )

        return {
            "concurso_uuid": str(concurso_uuid),
            "total_itens": len(itens),
        }, status.HTTP_201_CREATED
