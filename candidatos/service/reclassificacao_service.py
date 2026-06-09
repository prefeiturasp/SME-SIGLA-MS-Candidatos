"""Módulo service/reclassificacao_service."""
from __future__ import annotations
from typing import Any
import logging
from django.db import transaction
from sigla_sdk.context import get_correlation_id
from candidatos.models import ConcursoCandidato, ConcursoCandidatoReclassificacao
logger = logging.getLogger(__name__)

def _categoria_efetiva_calculada(cc: ConcursoCandidato) -> str:
    """Calcula a categoria_efetiva baseada nas classificações existentes e.

    nos históricos de desclassificação registrados.
    Prioridade: PCD > NNA > GERAL.
    """
    desclass_pcd = cc.historicos_reclassificacao.filter(desclassificado_de='PCD').exists()
    desclass_nna = cc.historicos_reclassificacao.filter(desclassificado_de='NNA').exists()
    has_pcd_ativo = cc.classificacao_pcd is not None and (not desclass_pcd)
    has_nna_ativo = cc.classificacao_nna is not None and (not desclass_nna)
    has_geral = cc.classificacao is not None
    if has_pcd_ativo:
        return 'PCD'
    if has_nna_ativo:
        return 'NNA'
    if has_geral:
        return 'GERAL'
    return 'GERAL'

@transaction.atomic
def aplicar_reclassificacao(*, candidato_uuid: Any, desclassificar_de: str, motivo: str='', executado_por: str='') -> tuple[ConcursoCandidato, ConcursoCandidatoReclassificacao]:
    """Aplica a reclassificação explícita (desclassificação de NNA/PCD) a um.

    ConcursoCandidato,
    registra histórico e atualiza categoria_efetiva.
    """
    logger.info('Aplicando reclassificação', extra={'correlation_id': get_correlation_id(), 'candidato_uuid': candidato_uuid, 'desclassificar_de': desclassificar_de, 'motivo': motivo, 'executado_por': executado_por})
    cc = ConcursoCandidato.objects.select_for_update().select_related('candidato').get(uuid=candidato_uuid)
    desclassificar_de = (desclassificar_de or '').upper()
    if desclassificar_de not in ('NNA', 'PCD'):
        raise ValueError('desclassificar_de inválido. Use "NNA" ou "PCD".')
    if desclassificar_de == 'NNA' and cc.classificacao_nna is None:
        raise ValueError('Candidato não possui classificação NNA.')
    if desclassificar_de == 'PCD' and cc.classificacao_pcd is None:
        raise ValueError('Candidato não possui classificação PCD.')
    if cc.historicos_reclassificacao.filter(desclassificado_de=desclassificar_de).exists():
        raise ValueError(f'Já há desclassificação registrada para {desclassificar_de}.')
    hist = ConcursoCandidatoReclassificacao.objects.create(concurso_candidato=cc, desclassificado_de=desclassificar_de, motivo=motivo or '', executado_por=executado_por or '')
    nova_categoria = _categoria_efetiva_calculada(cc)
    hist.nova_classificacao = nova_categoria
    hist.save(update_fields=['nova_classificacao'])
    if cc.categoria_efetiva != nova_categoria:
        cc.categoria_efetiva = nova_categoria
        cc.save(update_fields=['categoria_efetiva', 'atualizado_em'])
    return (cc, hist)
