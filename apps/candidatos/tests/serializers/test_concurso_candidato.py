"""Testes unitários dos serializers de concurso candidato."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from candidatos.models import ConcursoCandidatoReclassificacao
from candidatos.serializer.concurso_candidato import (
    BuscarPorCpfsSerializer,
    BuscarPorUuidsSerializer,
    ConcursoCandidatoCpfUuidSerializer,
    ConcursoCandidatoEliminadoSerializer,
    ConcursoCandidatoReclassificadoSerializer,
    ConcursoCandidatoSerializer,
    EliminarSerializer,
    ExtracaoDadosFiltroSerializer,
    ExtracaoDadosSerializer,
    HabilitadosCalculadosParamsSerializer,
    LoteItemSerializer,
    ReclassificarSerializer,
    SalvarLotesSerializer,
)

pytestmark = pytest.mark.django_db


def test_concurso_candidato_serializer_serializacao(concurso_candidato):
    """Testa serialização completa do ConcursoCandidatoSerializer."""
    ConcursoCandidatoReclassificacao.objects.create(
        concurso_candidato=concurso_candidato,
        desclassificado_de="NNA",
        nova_classificacao="GERAL",
        motivo="Teste",
        executado_por="admin",
    )
    data = ConcursoCandidatoSerializer(concurso_candidato).data
    assert data["codigo_inscricao"] == "001"
    assert data["concurso_candidato_uuid"] == str(concurso_candidato.uuid)
    assert data["concurso_uuid"] == str(concurso_candidato.lote.concurso_uuid)
    assert data["concurso_nome"] == concurso_candidato.lote.concurso_nome
    assert data["candidato"]["cpf"] == concurso_candidato.candidato.cpf
    assert data["candidato"]["nome"] == concurso_candidato.candidato.nome
    assert len(data["reclassificacoes"]) == 1
    assert data["reclassificacoes"][0]["desclassificado_de"] == "NNA"


def test_concurso_candidato_serializer_filtra_fields(concurso_candidato):
    """Testa DynamicFieldsSerializer filtrando campos."""
    data = ConcursoCandidatoSerializer(
        concurso_candidato, fields=["uuid", "codigo_inscricao"]
    ).data
    assert set(data.keys()) == {"uuid", "codigo_inscricao"}


def test_get_concurso_candidato_uuid_sem_uuid():
    """Testa get_concurso_candidato_uuid quando não há uuid."""
    serializer = ConcursoCandidatoSerializer()
    assert (
        serializer.get_concurso_candidato_uuid(SimpleNamespace(uuid=None))
        is None
    )


def test_get_concurso_uuid_do_objeto_e_sem_lote():
    """Testa get_concurso_uuid via atributo direto e ausência de lote."""
    serializer = ConcursoCandidatoSerializer()
    concurso_uuid = uuid4()
    assert (
        serializer.get_concurso_uuid(
            SimpleNamespace(concurso_uuid=concurso_uuid, lote=None)
        )
        == str(concurso_uuid)
    )
    assert serializer.get_concurso_uuid(SimpleNamespace(lote=None)) is None


def test_get_concurso_nome_sem_lote():
    """Testa get_concurso_nome quando não há lote."""
    serializer = ConcursoCandidatoSerializer()
    assert serializer.get_concurso_nome(SimpleNamespace(lote=None)) is None


def test_get_candidato_sem_candidato():
    """Testa get_candidato quando candidato é None."""
    serializer = ConcursoCandidatoSerializer()
    assert serializer.get_candidato(SimpleNamespace(candidato=None)) is None


def test_get_reclassificacoes_sem_historico_e_com_erro():
    """Testa get_reclassificacoes sem related e com exceção."""
    serializer = ConcursoCandidatoSerializer()
    assert (
        serializer.get_reclassificacoes(
            SimpleNamespace(historicos_reclassificacao=None)
        )
        == []
    )

    class HistoricoQuebrado:
        def all(self):
            raise RuntimeError("falha")

    assert (
        serializer.get_reclassificacoes(
            SimpleNamespace(historicos_reclassificacao=HistoricoQuebrado())
        )
        == []
    )


def test_buscar_por_uuids_serializer():
    """Testa validação do BuscarPorUuidsSerializer."""
    uuid_valido = uuid4()
    valido = BuscarPorUuidsSerializer(data={"uuids": [str(uuid_valido)]})
    assert valido.is_valid(), valido.errors
    assert valido.validated_data["uuids"] == [uuid_valido]

    invalido = BuscarPorUuidsSerializer(data={"uuids": []})
    assert invalido.is_valid() is False
    assert "uuids" in invalido.errors


def test_buscar_por_cpfs_serializer():
    """Testa validação do BuscarPorCpfsSerializer."""
    processo_uuid = uuid4()
    valido = BuscarPorCpfsSerializer(
        data={
            "cpfs": ["123.456.789-00"],
            "processo_uuid": str(processo_uuid),
        }
    )
    assert valido.is_valid(), valido.errors
    assert valido.validated_data["processo_uuid"] == processo_uuid

    sem_processo = BuscarPorCpfsSerializer(data={"cpfs": ["123.456.789-00"]})
    assert sem_processo.is_valid() is False
    assert "processo_uuid" in sem_processo.errors


def test_concurso_candidato_cpf_uuid_serializer(concurso_candidato):
    """Testa ConcursoCandidatoCpfUuidSerializer com e sem candidato."""
    data = ConcursoCandidatoCpfUuidSerializer(concurso_candidato).data
    assert data["uuid"] == str(concurso_candidato.uuid)
    assert data["cpf"] == concurso_candidato.candidato.cpf

    serializer = ConcursoCandidatoCpfUuidSerializer()
    assert serializer.get_cpf(SimpleNamespace(candidato=None)) is None


def test_habilitados_calculados_params_serializer():
    """Testa HabilitadosCalculadosParamsSerializer."""
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    valido = HabilitadosCalculadosParamsSerializer(
        data={
            "quantidade": 10,
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "codigo_cargo": "ABC",
        }
    )
    assert valido.is_valid(), valido.errors

    invalido = HabilitadosCalculadosParamsSerializer(
        data={"quantidade": 0, "concurso_uuid": str(concurso_uuid)}
    )
    assert invalido.is_valid() is False
    assert "quantidade" in invalido.errors
    assert "processo_uuid" in invalido.errors


def test_reclassificar_serializer():
    """Testa ReclassificarSerializer e o validate."""
    candidato_uuid = uuid4()
    serializer = ReclassificarSerializer(
        data={
            "candidato_uuid": str(candidato_uuid),
            "desclassificar_de": "NNA",
            "nova_classificacao": "GERAL",
            "motivo": "ok",
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["desclassificar_de"] == "NNA"

    invalido = ReclassificarSerializer(
        data={"candidato_uuid": str(candidato_uuid), "desclassificar_de": "X"}
    )
    assert invalido.is_valid() is False


def test_eliminar_serializer():
    """Testa EliminarSerializer."""
    candidato_uuid = uuid4()
    serializer = EliminarSerializer(
        data={"candidato_uuid": str(candidato_uuid), "motivo": "doc"}
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["motivo"] == "doc"

    invalido = EliminarSerializer(data={})
    assert invalido.is_valid() is False
    assert "candidato_uuid" in invalido.errors


def test_concurso_candidato_reclassificado_serializer(concurso_candidato):
    """Testa ConcursoCandidatoReclassificadoSerializer."""
    data = ConcursoCandidatoReclassificadoSerializer(concurso_candidato).data
    assert data["candidato"]["nome"] == concurso_candidato.candidato.nome
    assert data["candidato"]["cpf"] == concurso_candidato.candidato.cpf

    serializer = ConcursoCandidatoReclassificadoSerializer()
    assert serializer.get_candidato(SimpleNamespace(candidato=None)) is None


def test_concurso_candidato_eliminado_serializer(concurso_candidato):
    """Testa ConcursoCandidatoEliminadoSerializer."""
    data = ConcursoCandidatoEliminadoSerializer(concurso_candidato).data
    assert data["candidato"]["nome"] == concurso_candidato.candidato.nome
    assert data["candidato"]["email"] == concurso_candidato.candidato.email

    serializer = ConcursoCandidatoEliminadoSerializer()
    assert serializer.get_candidato(SimpleNamespace(candidato=None)) is None


def test_lote_item_e_salvar_lotes_serializer():
    """Testa LoteItemSerializer e SalvarLotesSerializer."""
    item = LoteItemSerializer(
        data={
            "lote": 1,
            "empresa": 2,
            "vaga": 3,
            "identificacao": "123",
            "chave_inscrito": "abc",
            "numfunc": "1",
            "numvinc": "2",
        }
    )
    assert item.is_valid(), item.errors

    concurso_uuid = uuid4()
    lote = SalvarLotesSerializer(
        data={
            "concurso_uuid": str(concurso_uuid),
            "lotes": [
                {
                    "lote": 1,
                    "empresa": 2,
                    "vaga": 3,
                    "identificacao": "123",
                }
            ],
        }
    )
    assert lote.is_valid(), lote.errors
    assert lote.validated_data["concurso_uuid"] == concurso_uuid

    invalido = SalvarLotesSerializer(
        data={"concurso_uuid": str(concurso_uuid), "lotes": []}
    )
    assert invalido.is_valid() is False


def test_extracao_dados_serializers():
    """Testa ExtracaoDadosFiltroSerializer e ExtracaoDadosSerializer."""
    processo_uuid = uuid4()
    filtro = ExtracaoDadosFiltroSerializer(
        data={"ano": 2024, "processo_uuids": [str(processo_uuid)]}
    )
    assert filtro.is_valid(), filtro.errors

    serializer = ExtracaoDadosSerializer(
        data={
            "concurso_uuid": str(uuid4()),
            "filtros": [{"ano": 2024, "processo_uuids": []}],
        }
    )
    assert serializer.is_valid(), serializer.errors

    vazio = ExtracaoDadosSerializer(data={})
    assert vazio.is_valid(), vazio.errors
    assert vazio.validated_data.get("filtros") == []
