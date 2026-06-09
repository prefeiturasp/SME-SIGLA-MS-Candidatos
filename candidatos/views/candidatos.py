"""Módulo views/candidatos."""
from __future__ import annotations
from typing import Any
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from candidatos.models import Candidato, ConcursoCandidato
from candidatos.serializers import CandidatoSerializer, CandidatosLoteCreateSerializer, ConcursoCandidatoSerializer
from candidatos.service.candidato_lote_service import processar_criacao_candidatos_lote

class CandidatoViewSet(viewsets.ModelViewSet):
    """Define CandidatoViewSet."""
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'genero', 'cidade', 'estado']
    search_fields = ['nome', 'cpf', 'email', 'cidade', 'rg', 'registro_funcional']
    ordering_fields = ['nome', 'data_nascimento', 'created_at']
    ordering = ['nome']

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Executa create.
        
        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.
            *args: Argumentos posicionais variáveis.
            **kwargs: Argumentos nomeados variáveis.
        
        Returns:
            Resposta HTTP com os dados serializados.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        input_serializer = CandidatosLoteCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        resp_data, status_code = processar_criacao_candidatos_lote(input_serializer.validated_data)
        return Response(resp_data, status=status_code)

    @action(methods=['get'], detail=False, url_path='buscar')
    def buscar(self, request: Any) -> Any:
        """Busca por nome, CPF, RG e/ou registro funcional na tabela.
        
        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.
        
        Returns:
            Resultado da operação.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        nome = request.query_params.get('nome', '').strip()
        cpf = request.query_params.get('cpf', '').strip()
        rg = request.query_params.get('rg', '').strip()
        registro_funcional = request.query_params.get('registro_funcional', '').strip()
        if not any([nome, cpf, rg, registro_funcional]):
            return Response({'detail': 'Informe pelo menos um parâmetro: nome, cpf, rg ou registro_funcional.'}, status=status.HTTP_400_BAD_REQUEST)
        q_obj = Q()
        if nome:
            q_obj &= Q(candidato__nome__icontains=nome)
        if cpf:
            q_obj &= Q(candidato__cpf__icontains=cpf)
        if rg:
            q_obj &= Q(candidato__rg__icontains=rg)
        if registro_funcional:
            q_obj &= Q(candidato__registro_funcional__icontains=registro_funcional)
        cc_qs = ConcursoCandidato.objects.filter(q_obj).select_related('candidato', 'lote').order_by('candidato__nome')[:300]
        cc_list = list(cc_qs)
        candidatos_por_uuid = {}
        for cc in cc_list:
            c = cc.candidato
            if c.uuid not in candidatos_por_uuid:
                candidatos_por_uuid[c.uuid] = {'candidato': c, 'concursos': []}
            candidatos_por_uuid[c.uuid]['concursos'].append(cc)  # type: ignore[attr-defined]
        resultado = []
        for c in candidatos_por_uuid.values():  # type: ignore[assignment]
            item = CandidatoSerializer(c['candidato']).data  # type: ignore[index]
            item['concursos'] = ConcursoCandidatoSerializer(c['concursos'], many=True).data  # type: ignore[index]
            resultado.append(item)
        return Response(resultado)
