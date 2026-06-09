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
from candidatos.service.exceptions import SalvarLotesException

logger = logging.getLogger(__name__)


@transaction.atomic
def salvar_lotes(concurso_uuid: str, lotes: list[dict[str, Any]]) -> int:
    """Grava dados de lote nos ConcursoCandidatos do concurso informado.
    
    Args:
        concurso_uuid: Parâmetro concurso uuid da operação.
        lotes: Parâmetro lotes da operação.
    
    Returns:
        Valor inteiro calculado.
    
    Raises:
        SalvarLotesException: Se ocorrer erro nesta operação.
    """
    erros: list[str] = []

    nro_lote_reset = lotes[0]["lote"]

    # 1. Reset: zera campos de lote dos registros com o mesmo numero_lote no concurso  # noqa: E501
    if nro_lote_reset:
        ConcursoCandidato.objects.filter(
            lote__concurso_uuid=concurso_uuid,
            numero_lote=nro_lote_reset,
        ).order_by("-criado_em").update(
            numero_lote=None,
            codigo_sigpec=None,
            numero_vaga=None,
        )

    cc_para_atualizar: list[ConcursoCandidato] = []
    candidatos_para_atualizar: list[Candidato] = []
    total_atualizados = 0

    for index, item in enumerate(lotes, start=1):
        linha = index
        identificacao = str(item.get("identificacao", "")).strip()

        # 2. Busca por chave_inscrito (= codigo_inscricao) no concurso
        cc = (
            ConcursoCandidato.objects.select_related("candidato")
            .filter(
                lote__concurso_uuid=concurso_uuid,
                codigo_inscricao=identificacao,
            )
            .order_by("-criado_em")
            .first()
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
        ConcursoCandidato.objects.bulk_update(
            cc_para_atualizar,
            ["numero_lote", "codigo_sigpec", "numero_vaga", "chave_inscrito"],
        )

    if candidatos_para_atualizar:
        Candidato.objects.bulk_update(
            candidatos_para_atualizar,
            ["registro_funcional", "vinculo"],
        )

    logger.info(
        "salvar_lotes: %d candidatos atualizados para concurso=%s",
        total_atualizados,
        concurso_uuid,
    )
    return total_atualizados
