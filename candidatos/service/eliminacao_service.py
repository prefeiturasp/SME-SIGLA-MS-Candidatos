import logging
from typing import Tuple, Optional
from django.db import transaction
from django.utils import timezone
from candidatos.models import ConcursoCandidato, ConcursoCandidatoEliminacao

logger = logging.getLogger(__name__)


@transaction.atomic
def aplicar_eliminacao(*, candidato_uuid, motivo: str = '', executado_por: str = '') -> Tuple[ConcursoCandidato, ConcursoCandidatoEliminacao]:
    cc = ConcursoCandidato.objects.select_for_update().get(uuid=candidato_uuid)
    if cc.eliminado:
        raise ValueError('Registro já está eliminado.')
    cc.eliminado = True
    cc.eliminado_em = timezone.now()
    cc.eliminado_motivo = motivo or ''
    cc.eliminado_por = executado_por or ''
    cc.save(update_fields=['eliminado', 'eliminado_em', 'eliminado_motivo', 'eliminado_por', 'atualizado_em'])
    hist = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc,
        motivo=motivo or '',
        executado_por=executado_por or '',
    )
    return cc, hist
