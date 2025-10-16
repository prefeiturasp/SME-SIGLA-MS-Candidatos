from django.db import models
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote
from candidatos.serializers import ConcursoCandidatoSerializer


class HabilitadosViewSet(viewsets.ModelViewSet):
    """
    ViewSet baseado em ConcursoCandidato.
    Suporta GET /habilitados/?concurso_uuid=<uuid>&geral=<val>&pcd=<val>&nna=<val>
    - geral -> filtra campo 'classificacao'
    - pcd   -> filtra campo 'classificacao_pcd'
    - nna   -> filtra campo 'classificacao_nna'
    """

    queryset = ConcursoCandidato.objects.select_related('candidato', 'lote').all()
    serializer_class = ConcursoCandidatoSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()

        concurso_uuid = self.request.query_params.get('concurso_uuid')
        if not concurso_uuid:
            # Sem concurso_uuid não retorna nada
            return ConcursoCandidato.objects.none()

        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )
        if not lote:
            return ConcursoCandidato.objects.none()
        qs = qs.filter(lote=lote)

        geral = self.request.query_params.get('geral')
        pcd = self.request.query_params.get('pcd')
        nna = self.request.query_params.get('nna')

        # Se nenhum limite foi informado, retorna todos do lote
        if geral in (None, '') and pcd in (None, '') and nna in (None, ''):
            return qs

        # Converte valores para int quando possível
        def to_int(value):
            try:
                return int(str(value))
            except Exception:
                return 0

        geral_n = to_int(geral)
        pcd_n = to_int(pcd)
        nna_n = to_int(nna)

        # Monta lista respeitando limites por categoria
        ids_incluidos = set()
        resultados = []

        if geral_n > 0:
            subset = (
                qs.exclude(classificacao__isnull=True)
                  .exclude(classificacao=None)
                  .order_by('classificacao', 'id')[:geral_n]
            )
            for obj in subset:
                if obj.id not in ids_incluidos:
                    ids_incluidos.add(obj.id)
                    resultados.append(obj.id)

        if pcd_n > 0:
            subset = (
                qs.exclude(classificacao_pcd__isnull=True)
                  .exclude(classificacao_pcd=None)
                  .order_by('classificacao_pcd', 'id')[:pcd_n]
            )
            for obj in subset:
                if obj.id not in ids_incluidos:
                    ids_incluidos.add(obj.id)
                    resultados.append(obj.id)

        if nna_n > 0:
            subset = (
                qs.exclude(classificacao_nna__isnull=True)
                  .exclude(classificacao_nna=None)
                  .order_by('classificacao_nna', 'id')[:nna_n]
            )
            for obj in subset:
                if obj.id not in ids_incluidos:
                    ids_incluidos.add(obj.id)
                    resultados.append(obj.id)

        # Ordena priorizando PCD (0), depois NNA (1) e por último demais (2)
        prioridade = models.Case(
            models.When(classificacao_pcd__isnull=False, then=models.Value(0)),
            models.When(classificacao_nna__isnull=False, then=models.Value(1)),
            default=models.Value(2),
            output_field=models.IntegerField(),
        )

        return (
            qs.filter(id__in=resultados)
              .annotate(_prio=prioridade)
              .order_by('_prio', 'classificacao_pcd', 'classificacao_nna', 'classificacao', 'id')
        )


    @action(detail=False, methods=['patch'], url_path='convocar')
    def convocar(self, request):
        """
        Atualiza múltiplos registros de ConcursoCandidato para convocados.
        Payload esperado:
        {
            "concurso_uuid": "...",
            "candidatos": ["uuid-1", "uuid-2", ...]
        }
        """
        concurso_uuid = request.data.get('concurso_uuid')
        candidatos = request.data.get('candidatos', [])

        if not concurso_uuid or not isinstance(candidatos, list):
            return Response({'detail': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)

        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )
        if not lote:
            return Response({'detail': 'Lote não encontrado para o concurso informado'}, status=status.HTTP_404_NOT_FOUND)

        qs = ConcursoCandidato.objects.filter(lote=lote, uuid__in=candidatos)
        atualizados = list(qs.values_list('uuid', flat=True))
        qs.update(foi_convocado=True, data_convocacao=timezone.now())

        return Response({'atualizados': [str(u) for u in atualizados], 'total': len(atualizados)})
