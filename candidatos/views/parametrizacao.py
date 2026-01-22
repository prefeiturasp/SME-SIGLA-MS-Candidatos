from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from candidatos.models import Parametrizacao
from candidatos.serializer import ParametrizacaoSerializer


class ParametrizacaoAtualView(APIView):
    """
    View customizada para trabalhar sempre com o registro mais recente.
    Suporta GET e PATCH em /api/v1/parametrizacao/
    """
    
    def get(self, request):
        """
        GET /api/v1/parametrizacao/
        Retorna o registro mais recente de parametrização.
        Se não existir, retorna None.
        """
        parametrizacao = Parametrizacao.objects.all().order_by('-criado_em').first()
        if parametrizacao:
            serializer = ParametrizacaoSerializer(parametrizacao)
            return Response(serializer.data)
        return Response(None)
    
    def patch(self, request):
        """
        PATCH /api/v1/parametrizacao/
        Atualiza o registro mais recente de parametrização.
        Se não existir, cria um novo.
        """
        parametrizacao = Parametrizacao.objects.all().order_by('-criado_em').first()
        
        if parametrizacao:
            serializer = ParametrizacaoSerializer(parametrizacao, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Se não existir, cria um novo
            serializer = ParametrizacaoSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

