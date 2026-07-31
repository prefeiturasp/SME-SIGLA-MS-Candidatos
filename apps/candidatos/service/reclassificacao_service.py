"""Módulo service/reclassificacao_service."""

from __future__ import annotations

import logging
from typing import Any

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
)
from candidatos.repository import (
    ConcursoCandidatoReclassificacaoRepository,
    ConcursoCandidatoRepository,
)
from django.db import transaction
from sigla_sdk.context import get_correlation_id

logger = logging.getLogger(__name__)


def _categoria_efetiva_calculada(cc: ConcursoCandidato) -> str:
    """Determina a categoria efetiva com base nas classificações e histórico.

    Args:
        cc: Registro de ConcursoCandidato a avaliar.

    Returns:
        Conteúdo textual gerado.
    """
    desclass_pcd = (
        ConcursoCandidatoReclassificacaoRepository.existe_desclassificacao(
            cc, "PCD"
        )
    )
    desclass_nna = (
        ConcursoCandidatoReclassificacaoRepository.existe_desclassificacao(
            cc, "NNA"
        )
    )
    has_pcd_ativo = cc.classificacao_pcd is not None and (not desclass_pcd)
    has_nna_ativo = cc.classificacao_nna is not None and (not desclass_nna)
    has_geral = cc.classificacao is not None
    if has_pcd_ativo:
        return "PCD"
    if has_nna_ativo:
        return "NNA"
    if has_geral:
        return "GERAL"
    return "GERAL"


def _reverter_por_mandado(
    *,
    cc: ConcursoCandidato,
    desclassificar_de: str,
    motivo: str = "",
    executado_por: str = "",
) -> tuple[ConcursoCandidato, ConcursoCandidatoReclassificacao]:
    """Reverte a desclassificação ativa de uma categoria por mandado.

    Cria um novo registro de histórico com ``mandado_judicial=True``,
    invertendo ``desclassificado_de`` e ``nova_classificacao`` do
    registro ativo (preservando-o como histórico), e recalcula a
    ``categoria_efetiva`` do candidato.

    Args:
        cc: ConcursoCandidato já bloqueado para atualização.
        desclassificar_de: Categoria a reverter (``NNA`` ou ``PCD``).
        motivo: Motivo/observação do mandado.
        executado_por: Usuário que executou a reversão.

    Returns:
        Tupla com o ConcursoCandidato e o novo histórico criado.

    Raises:
        ValueError: Se não houver desclassificação ativa a reverter.
    """
    hist = (
        ConcursoCandidatoReclassificacaoRepository.obter_ativa_por_categoria(
            cc, desclassificar_de
        )
    )
    if hist is None:
        raise ValueError(
            f"Não há desclassificação a reverter para {desclassificar_de}."
        )
    novo_hist = ConcursoCandidatoReclassificacaoRepository.criar(
        concurso_candidato=cc,
        desclassificado_de=hist.nova_classificacao,
        nova_classificacao=hist.desclassificado_de,
        mandado_judicial=True,
        motivo=motivo or "",
        executado_por=executado_por or "",
    )

    cc.categoria_efetiva = hist.desclassificado_de
    ConcursoCandidatoRepository.salvar(
        cc, campos_atualizacao=["categoria_efetiva", "atualizado_em"]
    )
    return (cc, novo_hist)


@transaction.atomic
def aplicar_reclassificacao(
    *,
    candidato_uuid: Any,
    desclassificar_de: str,
    motivo: str = "",
    executado_por: str = "",
    mandado_judicial: bool = False,
) -> tuple[ConcursoCandidato, ConcursoCandidatoReclassificacao]:
    """Aplica reclassificacao.

    Quando ``mandado_judicial`` é ``True``, reverte a desclassificação
    ativa da categoria informada: o registro existente é mantido como
    histórico, marcado com ``mandado_judicial=True``, e a
    ``categoria_efetiva`` do candidato é recalculada, devolvendo-o à
    categoria de origem.

    Args:
        candidato_uuid: UUID do ConcursoCandidato a reclassificar.
        desclassificar_de: Categoria de origem (``NNA`` ou ``PCD``).
        motivo: Motivo.
        executado_por: Executado por.
        mandado_judicial: Se ``True``, reverte a desclassificação
            existente por determinação judicial.

    Returns:
        Tupla com os objetos criados ou atualizados.

    Raises:
        ValueError: Se parâmetros forem inválidos ou operação negada.
    """
    logger.info(
        "Aplicando reclassificação",
        extra={
            "correlation_id": get_correlation_id(),
            "candidato_uuid": candidato_uuid,
            "desclassificar_de": desclassificar_de,
            "motivo": motivo,
            "executado_por": executado_por,
            "mandado_judicial": mandado_judicial,
        },
    )
    cc = ConcursoCandidatoRepository.obter_com_candidato_for_update(
        candidato_uuid
    )
    desclassificar_de = (desclassificar_de or "").upper()
    if desclassificar_de not in ("NNA", "PCD"):
        raise ValueError('desclassificar_de inválido. Use "NNA" ou "PCD".')
    if mandado_judicial:
        return _reverter_por_mandado(
            cc=cc,
            desclassificar_de=desclassificar_de,
            motivo=motivo,
            executado_por=executado_por,
        )
    if desclassificar_de == "NNA" and cc.classificacao_nna is None:
        raise ValueError("Candidato não possui classificação NNA.")
    if desclassificar_de == "PCD" and cc.classificacao_pcd is None:
        raise ValueError("Candidato não possui classificação PCD.")
    if ConcursoCandidatoReclassificacaoRepository.existe_desclassificacao(
        cc, desclassificar_de
    ):
        raise ValueError(
            f"Já há desclassificação registrada para {desclassificar_de}."
        )
    hist = ConcursoCandidatoReclassificacaoRepository.criar(
        concurso_candidato=cc,
        desclassificado_de=desclassificar_de,
        motivo=motivo or "",
        executado_por=executado_por or "",
    )
    nova_categoria = _categoria_efetiva_calculada(cc)
    hist.nova_classificacao = nova_categoria
    ConcursoCandidatoReclassificacaoRepository.salvar(
        hist, campos_atualizacao=["nova_classificacao"]
    )
    if cc.categoria_efetiva != nova_categoria:
        cc.categoria_efetiva = nova_categoria
        ConcursoCandidatoRepository.salvar(
            cc, campos_atualizacao=["categoria_efetiva", "atualizado_em"]
        )
    return (cc, hist)
