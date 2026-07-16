"""Serviço de importação de lotes de classificação (migração do legado.

MS_SES_Classificacao_SalvarMergeLotes).

Atualiza ConcursoCandidato com numero_lote, codigo_sigpec, numero_vaga
e atualiza Candidato.registro_funcional e Candidato.vinculo a partir dos dados
do arquivo de lote.
"""

import logging
from typing import Any

from django.db import transaction

from candidatos.models import ConcursoCandidato
from candidatos.models.candidato import Candidato
from candidatos.repository import (
    CandidatoRepository,
    ConcursoCandidatoRepository,
)
from candidatos.service.exceptions import SalvarLotesException

logger = logging.getLogger(__name__)


@transaction.atomic
def salvar_lotes(concurso_uuid: str, lotes: list[dict[str, Any]]) -> int:
    """Salva lotes.

    Args:
        concurso_uuid: UUID do concurso relacionado.
        lotes: Lista de lotes a persistir no serviço de candidatos.

    Returns:
        Quantidade de registros processados.

    Raises:
        SalvarLotesException: Se houver erro ao persistir os lotes.
    """
    erros: list[str] = []

    nro_lote_reset = lotes[0]["lote"]

    # 1. Reset: zera campos de lote dos registros com o mesmo numero_lote no concurso  # noqa: E501
    if nro_lote_reset:
        ConcursoCandidatoRepository.resetar_campos_lote_por_numero(
            concurso_uuid, nro_lote_reset
        )

    cc_para_atualizar: list[ConcursoCandidato] = []
    candidatos_para_atualizar: list[Candidato] = []
    total_atualizados = 0

    for index, item in enumerate(lotes, start=1):
        linha = index
        identificacao = str(item.get("identificacao", "")).strip()

        # 2. Busca por chave_inscrito (= codigo_inscricao) no concurso
        cc = ConcursoCandidatoRepository.obter_por_inscricao_no_concurso(
            concurso_uuid, identificacao
        )

        if not cc:
            logger.warning(
                "Candidato não encontrado para identificacao=%s no concurso=%s linha=%s",  # noqa: E501
                identificacao,
                concurso_uuid,
                linha,
            )
            erros.append(
                f"Linha: {linha} - Candidato com codigo_inscricao: {identificacao} não encontrado"  # noqa: E501
            )
            continue

        cc.numero_lote = item["lote"]
        cc.codigo_sigpec = item["empresa"]
        cc.numero_vaga = item["vaga"]
        chave_inscrito = str(item.get("chave_inscrito", "")).strip()
        cc.chave_inscrito = chave_inscrito or None

        cc_para_atualizar.append(cc)

        if cc.candidato:
            cc.candidato.registro_funcional = item["numfunc"]
            cc.candidato.vinculo = item["numvinc"]
            candidatos_para_atualizar.append(cc.candidato)

        total_atualizados += 1

    if erros:
        raise SalvarLotesException(
            mensagem="Falha ao salvar lotes. Nenhuma alteracao foi persistida.",  # noqa: E501
            detalhes="\n".join(erros),
        )

    if cc_para_atualizar:
        ConcursoCandidatoRepository.bulk_atualizar_campos_lote(
            cc_para_atualizar
        )

    if candidatos_para_atualizar:
        CandidatoRepository.bulk_atualizar_registro_vinculo(
            candidatos_para_atualizar
        )

    logger.info(
        "salvar_lotes: %d candidatos atualizados para concurso=%s",
        total_atualizados,
        concurso_uuid,
    )
    return total_atualizados
