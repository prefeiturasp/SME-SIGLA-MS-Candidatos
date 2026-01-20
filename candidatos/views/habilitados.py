import logging
from django.db import models
from django.core.exceptions import FieldError
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote
from candidatos.serializers import ConcursoCandidatoSerializer, BuscarPorUuidsSerializer, HabilitadosCalculadosParamsSerializer
from candidatos.service.calculo_habilitados_service import gerar_sequencia_convocados
from candidatos.service.escolhas_service import EscolhasService
from candidatos.service.ranking_service import atualizar_ranking, atualizar_ranking_escolha

logger = logging.getLogger(__name__)


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
    filterset_fields = {
        'processo_uuid': ['exact', 'in'],
        'codigo_cargo': ['exact', 'in'],
        'classificacao': ['exact', 'in'],
        'classificacao_pcd': ['exact', 'in'],
        'classificacao_nna': ['exact', 'in'],
    }

    @action(detail=False, methods=['get'], url_path='reconvocacao')
    def reconvocacao(self, request):
        """
        Endpoint para buscar candidatos habilitados para reconvocação.
        Suporta GET /habilitados/reconvocacao/?concurso_uuid=<uuid>&quantidade=<num>
        - concurso_uuid: UUID do concurso (obrigatório)
        - quantidade: Quantidade de candidatos a retornar (obrigatório)

        Busca escolhas com situação de reconvocação no microserviço de Escolhas
        e filtra apenas candidatos cujo uuid está na lista retornada.
        """
        # Busca reconvocações no microserviço de Escolhas
        try:
            reconvocoes = EscolhasService.buscar_reconvocacoes()
            # Extrai a lista de candidato_uuid da resposta
            candidato_uuids = [
                item.get('candidato_uuid') 
                for item in reconvocoes 
                if item.get('candidato_uuid') is not None
            ]
        except Exception as exc:
            logger.error(f"Erro ao buscar reconvocações no microserviço de Escolhas: {exc}")
            return Response(
                {'detail': 'Erro ao buscar reconvocações no microserviço de Escolhas'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        # Se não houver candidatos para reconvocação, retorna vazio
        if not candidato_uuids:
            serializer = self.get_serializer([], many=True)
            return Response(serializer.data)


        concurso_uuid = request.query_params.get('concurso_uuid')
        quantidade = request.query_params.get('quantidade')
        if not concurso_uuid:
            # Sem concurso_uuid não retorna nada
            serializer = self.get_serializer([], many=True)
            return Response(serializer.data)
        if not quantidade:
            return Response(
                {'detail': 'quantidade é obrigatória'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                return Response(
                    {'detail': 'quantidade deve ser um número positivo'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'detail': 'quantidade deve ser um número válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )
        if not lote:
            serializer = self.get_serializer([], many=True)
            return Response(serializer.data)

        # Filtrar apenas candidatos convocados E que estão na lista de reconvocações
        qs = ConcursoCandidato.objects.filter(lote=lote, foi_convocado=True, uuid__in=candidato_uuids)
        # Filtro opcional por código de cargo
        codigo_cargo = request.query_params.get('codigo_cargo')
        if codigo_cargo not in (None, ''):
            qs = qs.filter(codigo_cargo=codigo_cargo)

        # Ordena priorizando PCD (0), depois NNA (1) e por último demais (2), e limita pela quantidade
        prioridade = models.Case(
            models.When(classificacao_pcd__isnull=False, then=models.Value(0)),
            models.When(classificacao_nna__isnull=False, then=models.Value(1)),
            default=models.Value(2),
            output_field=models.IntegerField(),
        )

        qs_final = qs.annotate(_prio=prioridade).order_by(
            '_prio', 'classificacao_pcd', 'classificacao_nna', 'classificacao', 'id'
        )[:quantidade]
        atualizar_ranking(list(qs_final))
        atualizar_ranking_escolha(list(qs_final))
        serializer = self.get_serializer(qs_final, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reposicao')
    def reposicao(self, request):
        """
        Endpoint para buscar candidatos habilitados para reposição.
        Busca candidatos que já foram convocados (foi_convocado=True) do lote mais recente do concurso.

        Suporta GET /habilitados/reposicao/?concurso_uuid=<uuid>&geral=<val>&pcd=<val>&nna=<val>
        - concurso_uuid: UUID do concurso (obrigatório)
        - geral -> filtra campo 'classificacao'
        - pcd   -> filtra campo 'classificacao_pcd'
        - nna   -> filtra campo 'classificacao_nna'
        """
        concurso_uuid = request.query_params.get('concurso_uuid')

        if not concurso_uuid:
            return Response(
                {'detail': 'concurso_uuid é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Busca o lote mais recente do concurso
        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )

        if not lote:
            serializer = self.get_serializer([], many=True)
            return Response(serializer.data)

        # Base: candidatos não convocados do lote
        qs = ConcursoCandidato.objects.select_related('candidato', 'lote').filter(lote=lote, foi_convocado=False)

        # Filtro opcional por código de cargo
        codigo_cargo = request.query_params.get('codigo_cargo')
        if codigo_cargo not in (None, ''):
            qs = qs.filter(codigo_cargo=codigo_cargo)

        geral = request.query_params.get('geral')
        pcd = request.query_params.get('pcd')
        nna = request.query_params.get('nna')

        # Se nenhum limite foi informado, retorna todos do lote
        if geral in (None, '') and pcd in (None, '') and nna in (None, ''):
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)

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

        # Ordena somente pela classificação
        qs_final = (
            qs.filter(id__in=resultados)
              .order_by('classificacao')
        )

        atualizar_ranking(list(qs_final))
        atualizar_ranking_escolha(list(qs_final))
        serializer = self.get_serializer(qs_final, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='convocar')
    def convocar(self, request):
        """
        Atualiza múltiplos registros de ConcursoCandidato quanto ao status de convocação.
        Payload esperado:
        {
            "concurso_uuid": "...",
            "candidatos": ["uuid-1", "uuid-2", ...],
            "foi_convocado": true|false   # opcional; default: true
        }
        """
        concurso_uuid = request.data.get('concurso_uuid')
        processo_uuid = request.data.get('processo_uuid')
        candidatos = request.data.get('candidatos', [])

        if not (concurso_uuid or processo_uuid) or not isinstance(candidatos, list):
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
        qs.update(foi_convocado=True, processo_uuid=processo_uuid, data_convocacao=timezone.now())

        return Response({
            'atualizados': [str(u) for u in atualizados],
            'total': len(atualizados)
        })

    @action(detail=False, methods=['patch'], url_path='desconvocar')
    def desconvocar(self, request):
        """
        Marca como NÃO convocados todos os registros que pertencem ao processo (lote)
        informado e correspondem ao código de cargo fornecido.

        Payload esperado:
        {
            "processo_uuid": "...",      # ou "concurso_uuid"
            "codigo_cargo": "12345"
        }
        """
        processo_uuid = request.data.get('processo_uuid') or request.data.get('concurso_uuid')
        codigo_cargo = request.data.get('codigo_cargo')

        if not processo_uuid or not codigo_cargo:
            return Response({'detail': 'processo_uuid (ou concurso_uuid) e codigo_cargo são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        qs = ConcursoCandidato.objects.filter(processo_uuid=processo_uuid, codigo_cargo=codigo_cargo, foi_convocado=True)
        atualizados = list(qs.values_list('uuid', flat=True))
        qs.update(foi_convocado=False, data_convocacao=None, processo_uuid=None)

        return Response({
            'desconvocados': [str(u) for u in atualizados],
            'total': len(atualizados),
            'processo_uuid': str(processo_uuid),
            'codigo_cargo': str(codigo_cargo),
        })

    @action(detail=False, methods=['post'], url_path='buscar-por-uuids')
    def buscar_por_uuids(self, request):
        """
        Busca candidatos habilitados por uma lista de UUIDs.
        
        Payload esperado:
        {
            "uuids": ["uuid-1", "uuid-2", "uuid-3", ...]
        }

        Retorna os dados serializados dos candidatos encontrados.
        """
        # Validação usando serializer
        input_serializer = BuscarPorUuidsSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        uuids = input_serializer.validated_data['uuids']
        order_by_param = request.query_params.get('order_by') or 'classificacao'

        # Busca os candidatos habilitados pelos UUIDs fornecidos
        try:
            queryset = (
                ConcursoCandidato.objects
                .filter(uuid__in=uuids)
                .order_by(order_by_param)
                .select_related('candidato', 'lote')
            )
        except FieldError:
            return Response(
                {'detail': 'Parâmetro order_by inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'results': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='calculados')
    def calculados(self, request):
        """
        Endpoint placeholder para cálculo de sequência de convocação.
        Por enquanto retorna um dict vazio.
        """
        params = HabilitadosCalculadosParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        quantidade = params.validated_data['quantidade']
        concurso_uuid = str(params.validated_data['concurso_uuid'])
        codigo_cargo = params.validated_data['codigo_cargo']
        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )
        if not lote:
            return Response({'detail': 'Lote não encontrado para o concurso_uuid informado'}, status=status.HTTP_404_NOT_FOUND)
        # Buscar escolhas e extrair apenas os candidato_uuid
        try:
            escolhas = EscolhasService.buscar_escolhas(concurso_uuid=concurso_uuid)
            escolhas_candidato_uuids = [
                item.get('candidato_uuid')
                for item in escolhas
                if item.get('candidato_uuid') is not None
            ]
        except Exception as exc:
            logger.error(f"Erro ao buscar escolhas: {exc}")
            escolhas_candidato_uuids = []
        itens = gerar_sequencia_convocados(quantidade, lote, escolhas_candidato_uuids, codigo_cargo)
        serializer = self.get_serializer(itens, many=True)

        return Response({
            'quantidade': quantidade,
            'concurso_uuid': str(concurso_uuid),
            'lote_uuid': str(lote.uuid),
            'results': serializer.data
        })
