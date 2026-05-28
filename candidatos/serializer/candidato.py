from rest_framework import serializers

from candidatos.models import Candidato

from .concurso_candidato import ConcursoCandidatoSerializer


class CandidatoSerializer(serializers.ModelSerializer):
    concursos = ConcursoCandidatoSerializer(many=True, read_only=True)

    class Meta:
        model = Candidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]


class CandidatoConcursoCreateSerializer(serializers.Serializer):
    nome = serializers.CharField(allow_blank=True, required=False)
    data_nascimento = serializers.CharField(required=False, allow_blank=True)
    sexo = serializers.CharField(required=False, allow_blank=True)
    rg = serializers.CharField(required=False, allow_blank=True)
    cpf = serializers.CharField(required=False, allow_blank=True)
    registro_funcional = serializers.CharField(
        required=False, allow_blank=True
    )
    vinculo = serializers.CharField(required=False, allow_blank=True)
    endereco = serializers.CharField(required=False, allow_blank=True)
    numero = serializers.CharField(required=False, allow_blank=True)
    complemento = serializers.CharField(required=False, allow_blank=True)
    bairro = serializers.CharField(required=False, allow_blank=True)
    cep = serializers.CharField(required=False, allow_blank=True)
    cidade = serializers.CharField(required=False, allow_blank=True)
    uf = serializers.CharField(required=False, allow_blank=True)
    telefone = serializers.CharField(required=False, allow_blank=True)
    celular = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    codigo_inscricao = serializers.CharField()
    classificacao = serializers.CharField(required=False, allow_blank=True)
    pontos = serializers.CharField(required=False, allow_blank=True)
    classificacao_deficiente = serializers.CharField(
        required=False, allow_blank=True
    )
    opcao_concurso = serializers.CharField(required=False, allow_blank=True)
    codigo_cargo = serializers.CharField(required=False, allow_blank=True)
    cota = serializers.CharField(required=False, allow_blank=True)
    descricao_cargo = serializers.CharField(required=False, allow_blank=True)
    df = serializers.CharField(required=False, allow_blank=True)
    classificacao_nna = serializers.CharField(required=False, allow_blank=True)
    ano_concurso = serializers.CharField(required=False, allow_blank=True)
    observacao = serializers.CharField(required=False, allow_blank=True)


class CandidatosLoteCreateSerializer(serializers.Serializer):
    concurso_uuid = serializers.UUIDField()
    concurso_nome = serializers.CharField(allow_blank=True, required=False)
    candidatos = CandidatoConcursoCreateSerializer(many=True)
