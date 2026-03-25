"""
Serviço de importação de lotes de classificação (migração do legado MS_SES_Classificacao_SalvarMergeLotes).

Atualiza ConcursoCandidato com numero_lote, codigo_sigpec, numero_vaga
e atualiza Candidato.registro_funcional e Candidato.vinculo a partir dos dados do arquivo de lote.
"""
import logging
from typing import Any
from django.db import transaction

from candidatos.models import ConcursoCandidato
from candidatos.models.candidato import Candidato

logger = logging.getLogger(__name__)


class SalvarLotesException(Exception):
    def __init__(self, mensagem: str, erros_por_linha: list[dict[str, Any]] | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.erros_por_linha = erros_por_linha or []

    def __str__(self) -> str:
        return self.mensagem


@transaction.atomic
def salvar_lotes(concurso_uuid: str, lotes: list[dict[str, Any]]) -> int:
    """
    Grava dados de lote nos ConcursoCandidatos do concurso informado.

    1. Reset: zera campos de lote de todos os registros que já tinham o mesmo numero_lote no concurso.
    2. Para cada item do arquivo, busca ConcursoCandidato por chave_inscrito (= codigo_inscricao).
    3. Atualiza ConcursoCandidato (numero_lote, codigo_sigpec, numero_vaga)
       e Candidato (registro_funcional, vinculo).
    4. Retorna total de candidatos atualizados.
    """ 

    erros_por_linha: list[dict[str, Any]] = []

    primeiro_lote = lotes[0]
    try:
        nro_lote_reset = int(primeiro_lote.get('lote'))
    except (TypeError, ValueError):
        raise SalvarLotesException(
            'Campo lote invalido na linha 1.',
            erros_por_linha=[
                {
                    'linha': 1,
                    'identificacao': str(primeiro_lote.get('identificacao', '')).strip(),
                    'mensagem': 'Campo lote deve ser numerico.',
                }
            ],
        )
    
    # 1. Reset: zera campos de lote dos registros com o mesmo numero_lote no concurso
    if nro_lote_reset:
        ConcursoCandidato.objects.filter(
            lote__concurso_uuid=concurso_uuid,
            numero_lote=nro_lote_reset,
        ).update(
            numero_lote=None,
            codigo_sigpec=None,
            numero_vaga=None,
        )

    cc_para_atualizar: list[ConcursoCandidato] = []
    candidatos_para_atualizar: list[Candidato] = []
    total_atualizados = 0

    for index, item in enumerate(lotes, start=1):
        linha = index
        identificacao = str(item.get('identificacao', '')).strip()

        # 2. Busca por chave_inscrito (= codigo_inscricao) no concurso
        cc = (
            ConcursoCandidato.objects
            .select_related('candidato')
            .filter(
                lote__concurso_uuid=concurso_uuid,
                codigo_inscricao=identificacao,
            )
            .first()
        )

        if not cc:
            logger.warning(
                'Candidato não encontrado para identificacao=%s no concurso=%s linha=%s',
                identificacao,
                concurso_uuid,
                linha,
            )
            erros_por_linha.append(
                {
                    'linha': linha,
                    'identificacao': identificacao,
                    'mensagem': f'Candidato com a identificacao {identificacao} nao encontrado.',
                }
            )
            continue

        try:
            cc.numero_lote = int(item.get('lote')) if item.get('lote') is not None else None
            cc.codigo_sigpec = int(item.get('empresa')) if item.get('empresa') is not None else None
            cc.numero_vaga = int(item.get('vaga')) if item.get('vaga') is not None else None
            chave_inscrito = str(item.get('chave_inscrito', '')).strip()
            cc.chave_inscrito = chave_inscrito or None
        except (TypeError, ValueError):
            erros_por_linha.append(
                {
                    'linha': linha,
                    'identificacao': identificacao,
                    'mensagem': 'Campos lote, empresa e vaga devem ser numericos.',
                }
            )
            continue

        cc_para_atualizar.append(cc)

        candidato = cc.candidato
        if candidato:
            candidato.registro_funcional = str(item.get('numfunc', '')).strip()
            candidato.vinculo = str(item.get('numvinc', '')).strip()
            candidatos_para_atualizar.append(candidato)

        total_atualizados += 1

    if erros_por_linha:
        raise SalvarLotesException(
            mensagem='Falha ao salvar lotes. Nenhuma alteracao foi persistida.',
            erros_por_linha=erros_por_linha,
        )

    if cc_para_atualizar:
        ConcursoCandidato.objects.bulk_update(
            cc_para_atualizar,
            ['numero_lote', 'codigo_sigpec', 'numero_vaga', 'chave_inscrito'],
        )

    if candidatos_para_atualizar:
        Candidato.objects.bulk_update(
            candidatos_para_atualizar,
            ['registro_funcional', 'vinculo'],
        )

    logger.info('salvar_lotes: %d candidatos atualizados para concurso=%s', total_atualizados, concurso_uuid)
    return total_atualizados
