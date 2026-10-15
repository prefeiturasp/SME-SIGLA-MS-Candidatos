"""Módulo serializer/candidato."""

from candidatos.models import Candidato
from rest_framework import serializers

from .concurso_candidato import ConcursoCandidatoSerializer
from .descricoes import DESCRICOES_CANDIDATO, DESCRICOES_HABILITADO


class CandidatoSerializer(serializers.ModelSerializer):
    """Candidato com os seus habilitados."""

    concursos = ConcursoCandidatoSerializer(
        many=True,
        read_only=True,
        help_text=(
            "Habilitados do candidato: uma inscrição por concurso e cargo."
        ),
    )

    class Meta:
        """Representa Meta."""

        model = Candidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]
        extra_kwargs = DESCRICOES_CANDIDATO


class CandidatoConcursoCreateSerializer(serializers.Serializer):
    """Linha da lista de habilitados: dados do candidato e da inscrição."""

    nome = serializers.CharField(
        allow_blank=True, required=False, **DESCRICOES_CANDIDATO["nome"]
    )
    data_nascimento = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Data de nascimento no formato `DD/MM/AAAA`. Ausente ou "
            "inválida, é gravada como `1900-01-01`."
        ),
    )
    sexo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Código do sexo: `1` (masculino) ou `2` (feminino). Qualquer "
            "outro valor deixa o gênero em branco."
        ),
    )
    rg = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["rg"]
    )
    cpf = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "CPF, com ou sem máscara. Identifica o candidato: se o CPF já "
            "existe, os dados pessoais são atualizados."
        ),
    )
    registro_funcional = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Registro funcional (RF) do candidato que já é servidor.",
    )
    vinculo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Número do vínculo funcional do servidor.",
    )
    endereco = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["endereco"]
    )
    numero = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["numero"]
    )
    complemento = serializers.CharField(
        required=False,
        allow_blank=True,
        **DESCRICOES_CANDIDATO["complemento"],
    )
    bairro = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["bairro"]
    )
    cep = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["cep"]
    )
    cidade = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["cidade"]
    )
    uf = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Sigla da unidade federativa, com 2 letras. Gravada no campo "
            "`estado` do candidato."
        ),
    )
    telefone = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["telefone"]
    )
    celular = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["celular"]
    )
    email = serializers.EmailField(
        required=False, allow_blank=True, **DESCRICOES_CANDIDATO["email"]
    )

    codigo_inscricao = serializers.CharField(
        **DESCRICOES_HABILITADO["codigo_inscricao"]
    )
    classificacao = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Classificação na lista geral, como texto numérico. Vazio ou "
            "não numérico grava nulo."
        ),
    )
    pontos = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Pontuação obtida, como texto numérico. Vazio ou inválido "
            "grava 0."
        ),
    )
    classificacao_deficiente = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Classificação na lista PCD, como texto numérico. Quando "
            "preenchida, a categoria efetiva do habilitado é `PCD`."
        ),
    )
    opcao_concurso = serializers.CharField(
        required=False,
        allow_blank=True,
        **DESCRICOES_HABILITADO["opcao_concurso"],
    )
    codigo_cargo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Código do cargo. Com o CPF e o concurso, identifica o "
            "habilitado: a mesma combinação atualiza o registro existente."
        ),
    )
    cota = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_HABILITADO["cota"]
    )
    descricao_cargo = serializers.CharField(
        required=False,
        allow_blank=True,
        **DESCRICOES_HABILITADO["descricao_cargo"],
    )
    df = serializers.CharField(
        required=False, allow_blank=True, **DESCRICOES_HABILITADO["df"]
    )
    classificacao_nna = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Classificação na lista NNA, como texto numérico. Quando "
            "preenchida e sem classificação PCD, a categoria efetiva do "
            "habilitado é `NNA`."
        ),
    )
    ano_concurso = serializers.CharField(
        required=False,
        allow_blank=True,
        **DESCRICOES_HABILITADO["ano_concurso"],
    )
    observacao = serializers.CharField(
        required=False,
        allow_blank=True,
        **DESCRICOES_HABILITADO["observacao"],
    )


class CandidatosLoteCreateSerializer(serializers.Serializer):
    """Lista de habilitados de um concurso, para carga em lote."""

    concurso_uuid = serializers.UUIDField(
        help_text="UUID do concurso (MS-Concursos) a que a lista pertence."
    )
    concurso_nome = serializers.CharField(
        allow_blank=True,
        required=False,
        help_text="Nome do concurso, gravado em cada habilitado.",
    )
    mandado_judicial = serializers.BooleanField(
        required=False,
        allow_null=True,
        default=False,
        help_text=(
            "Aceito por compatibilidade. O valor gravado não depende dele: "
            "os habilitados criados ficam com `mandado_judicial` verdadeiro "
            "quando o concurso já tinha habilitados antes desta carga e "
            "falso na primeira carga."
        ),
    )
    candidatos = CandidatoConcursoCreateSerializer(
        many=True, help_text="Linhas da lista, uma por inscrição."
    )
