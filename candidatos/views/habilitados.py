from django.db import models
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote
<<<<<<< Updated upstream
from candidatos.serializers import ConcursoCandidatoSerializer, BuscarPorUuidsSerializer
=======
from candidatos.serializers import ConcursoCandidatoSerializer, BuscarPorUuidsSerializer, HabilitadosCalculadosParamsSerializer
from candidatos.service.calculo_habilitados_service import gerar_sequencia_convocados
from candidatos.service.escolhas_service import EscolhasService

logger = logging.getLogger(__name__)
>>>>>>> Stashed changes


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
        # Filtrar apenas candidatos não convocados
        qs = qs.filter(lote=lote, foi_convocado=False)

        # Filtro opcional por código de cargo
        codigo_cargo = self.request.query_params.get('codigo_cargo')
        if codigo_cargo not in (None, ''):
            qs = qs.filter(codigo_cargo=codigo_cargo)

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
        
        # Busca os candidatos habilitados pelos UUIDs fornecidos
        queryset = ConcursoCandidato.objects.filter(
            uuid__in=uuids
        ).order_by('classificacao').select_related('candidato', 'lote')
        
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
        lote = (
            ConcursoCandidatosLote.objects
            .filter(concurso_uuid=concurso_uuid)
            .order_by('-criado_em')
            .first()
        )
        if not lote:
            return Response({'detail': 'Lote não encontrado para o concurso_uuid informado'}, status=status.HTTP_404_NOT_FOUND)
        itens = gerar_sequencia_convocados(quantidade, lote)
        serializer = self.get_serializer(itens, many=True)
        # Monta uma tabela visual com pipes e underlines: duas colunas (Posição | Tipo)
        linhas_brutas = []
        for candidato in serializer.data:
            # Define o tipo com base nas classificações de cota
            tipo = "GERAL"
            if candidato.get('classificacao_nna'):
                tipo = "NNA"
            elif candidato.get('classificacao_pcd'):
                tipo = "PCD"
            posicao = candidato.get('ranking') or candidato.get('classificacao') or ""
            linhas_brutas.append((str(posicao), tipo))

        # Calcula larguras para alinhamento (posicao direita, tipo esquerda)
        pos_w = max(len("Posicao"), *(len(p) for p, _ in linhas_brutas)) if linhas_brutas else len("Posicao")
        tipo_w = max(len("Tipo"), *(len(t) for _, t in linhas_brutas)) if linhas_brutas else len("Tipo")

        header = f"| {'Posicao':>{pos_w}} | {'Tipo':<{tipo_w}} |"
        underline = f"|{'-'*(pos_w+2)}|{'-'*(tipo_w+2)}|"
        linhas = [header, underline]
        for p, t in linhas_brutas:
            linhas.append(f"| {p:>{pos_w}} | {t:<{tipo_w}} |")
            linhas.append(underline)
        tabela = "\n".join(linhas)
        # print(tabela)
        # # Salva a mesma tabela em arquivo texto (sobrescrevendo)
        # try:
        #     from pathlib import Path
        #     out_path = Path(__file__).resolve().parent / "tabela_calculados.txt"
        #     with out_path.open("w", encoding="utf-8") as f:
        #         f.write(tabela)
        # except Exception:
        #     pass

        return Response({
            'quantidade': quantidade,
            'concurso_uuid': str(concurso_uuid),
            'lote_uuid': str(lote.uuid),
            'results': serializer.data
        })
