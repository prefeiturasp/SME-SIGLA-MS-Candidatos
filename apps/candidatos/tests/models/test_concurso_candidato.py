"""Testes unitários para o modelo ConcursoCandidato."""

from uuid import uuid4

import pytest
from candidatos.models import ConcursoCandidato
from candidatos.models.concurso_candidato import CATEGORIA_CHOICES
from django.utils import timezone

pytestmark = pytest.mark.django_db


def test_concurso_candidato_cria_com_campos_obrigatorios(
    concurso_uuid, candidato
):
    """Testa criação do concurso candidato com campos obrigatórios."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="001",
    )
    assert cc.candidato == candidato
    assert cc.concurso_uuid == concurso_uuid
    assert cc.concurso_nome == "Concurso Teste"
    assert cc.codigo_inscricao == "001"
    assert cc.uuid is not None
    assert cc.criado_em is not None
    assert cc.esta_ativo is True


def test_concurso_candidato_cria_com_valores_padrao(concurso_uuid, candidato):
    """Testa valores padrão do concurso candidato."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="002",
    )
    assert cc.pontos == 0.0
    assert cc.foi_convocado is False
    assert cc.ranking == 0
    assert cc.ranking_escolha == 0
    assert cc.categoria_efetiva == "GERAL"
    assert cc.promovido_para_geral is False
    assert cc.eliminado is False
    assert cc.eliminado_motivo == ""
    assert cc.eliminado_por == ""


def test_concurso_candidato_cria_sem_concurso_uuid(candidato):
    """Testa criação do concurso candidato sem concurso_uuid."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        codigo_inscricao="003",
    )
    assert cc.concurso_uuid is None


def test_concurso_candidato_representacao_str(concurso_uuid, candidato):
    """Testa a representação textual do concurso candidato."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="001",
        classificacao=10,
        classificacao_pcd=2,
        classificacao_nna=3,
        ranking=5,
    )
    esperado = f"{candidato.nome} - {cc.uuid} - 10 - 2 - 3 - 5"
    assert str(cc) == esperado


def test_concurso_candidato_meta_opcoes():
    """Testa as opções Meta do model ConcursoCandidato."""
    assert ConcursoCandidato._meta.verbose_name == "Concurso do Candidato"
    assert (
        ConcursoCandidato._meta.verbose_name_plural
        == "Concursos dos Candidatos"
    )
    assert ConcursoCandidato._meta.ordering == ["-criado_em"]


def test_concurso_candidato_categoria_choices():
    """Testa as choices de categoria efetiva."""
    assert CATEGORIA_CHOICES == (
        ("GERAL", "GERAL"),
        ("NNA", "NNA"),
        ("PCD", "PCD"),
    )


def test_concurso_candidato_related_name_concursos(candidato):
    """Testa o related_name concursos no candidato."""
    ConcursoCandidato.objects.create(
        candidato=candidato, codigo_inscricao="001"
    )
    ConcursoCandidato.objects.create(
        candidato=candidato, codigo_inscricao="002"
    )
    assert candidato.concursos.count() == 2


def test_concurso_candidato_filtra_por_concurso_uuid(
    concurso_uuid, candidato, criar_candidato
):
    """Testa filtro por concurso_uuid."""
    outro = criar_candidato(nome="Outro", cpf="222.222.222-22")
    ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="001",
    )
    ConcursoCandidato.objects.create(
        candidato=outro,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="002",
    )
    assert (
        ConcursoCandidato.objects.filter(concurso_uuid=concurso_uuid).count()
        == 2
    )


def test_concurso_candidato_update_convocacao(concurso_uuid, candidato):
    """Testa o update de convocação do concurso candidato."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="001",
    )
    processo_uuid = uuid4()
    agora = timezone.now()
    cc.foi_convocado = True
    cc.processo_uuid = processo_uuid
    cc.data_convocacao = agora
    cc.save()
    cc.refresh_from_db()
    assert cc.foi_convocado is True
    assert cc.processo_uuid == processo_uuid
    assert cc.data_convocacao is not None


def test_concurso_candidato_marca_eliminado(concurso_uuid, candidato):
    """Testa a marcação de eliminado no concurso candidato."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="001",
    )
    cc.eliminado = True
    cc.eliminado_em = timezone.now()
    cc.eliminado_motivo = "Documentação incompleta"
    cc.eliminado_por = "admin"
    cc.save()
    cc.refresh_from_db()
    assert cc.eliminado is True
    assert cc.eliminado_motivo == "Documentação incompleta"
    assert cc.eliminado_por == "admin"
    assert cc.eliminado_em is not None


def test_concurso_candidato_cascade_delete_candidato(concurso_uuid, candidato):
    """Testa cascade delete ao remover o candidato."""
    ConcursoCandidato.objects.create(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao="001",
    )
    assert ConcursoCandidato.objects.count() == 1
    candidato.delete()
    assert ConcursoCandidato.objects.count() == 0
