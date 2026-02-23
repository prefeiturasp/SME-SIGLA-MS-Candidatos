import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote
from candidatos.serializers import ConcursoCandidatoEliminadoSerializer

logger = logging.getLogger(__name__)


class EliminadosViewSet(viewsets.ViewSet):
    """
    Endpoint para listar candidatos eliminados por concurso_uuid e processo_uuid,
    no mesmo padrão do endpoint de reclassificados.
    GET /eliminados/?concurso_uuid=<uuid>&processo_uuid=<uuid>
    Retorna um dicionário separado por tipo de classificação:
    {
      "geral": [...],
      "nna": [...],
      "pcd": [...]
    }
    """

    def list(self, request):
        concurso_uuid = request.query_params.get('concurso_uuid')
        classificacao_max = request.query_params.get('classificacao_max')
        classificacao_min = request.query_params.get('classificacao_min')
        if not concurso_uuid or not classificacao_max or not classificacao_min:
            return Response({'detail': 'concurso_uuid, classificacao_max e classificacao_min são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        # Usa o último lote do concurso
        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )
        if not lote:
            return Response({'geral': [], 'nna': [], 'pcd': []})

        # Base: candidatos eliminados deste lote, vinculados a histórico de eliminação do processo informado
        base = (
            ConcursoCandidato.objects
            .select_related('candidato', 'lote')
            .filter(lote=lote, eliminado=True)
            .filter(classificacao__lte=classificacao_max, classificacao__gte=classificacao_min)
        ).distinct()

        # Separar por tipo de classificação
        qs_nna = base.filter(classificacao_nna__isnull=False).distinct()
        qs_pcd = base.filter(classificacao_pcd__isnull=False).distinct()
        ids_excluir = list(qs_nna.values_list('id', flat=True)) + list(qs_pcd.values_list('id', flat=True))
        qs_geral = base.exclude(id__in=ids_excluir).filter(classificacao__isnull=False).distinct()

        data = {
            'geral': ConcursoCandidatoEliminadoSerializer(qs_geral, many=True).data,
            'nna': ConcursoCandidatoEliminadoSerializer(qs_nna, many=True).data,
            'pcd': ConcursoCandidatoEliminadoSerializer(qs_pcd, many=True).data,
        }
        return Response(data)

