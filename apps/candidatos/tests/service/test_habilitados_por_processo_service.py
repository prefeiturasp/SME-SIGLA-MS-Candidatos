"""Testes do HabilitadosPorProcessoService."""

from __future__ import annotations

import uuid
from unittest.mock import patch

from candidatos.service.habilitados_por_processo_service import (
    HabilitadosPorProcessoService,
)

REPO_LISTAR = (
    "candidatos.service.habilitados_por_processo_service."
    "ConcursoCandidatoRepository.listar_convocados_por_processos"
)


def test_montar_lista_vazia_retorna_dict_vazio():
    """Sem processo_uuids, retorna dicionário vazio."""
    assert (
        HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga([])
        == {}
    )


@patch(REPO_LISTAR)
def test_montar_inicializa_blocos_mesmo_sem_rows(mock_listar):
    """Processos sem convocados vêm com totais zerados."""
    mock_listar.return_value = []
    pid = str(uuid.uuid4())

    resultado = HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga(
        [pid]
    )

    assert set(resultado.keys()) == {pid}
    assert resultado[pid] == {
        "GERAL": {"total": 0, "candidatos_uuids": []},
        "NNA": {"total": 0, "candidatos_uuids": []},
        "PCD": {"total": 0, "candidatos_uuids": []},
    }
    mock_listar.assert_called_once_with([pid])


@patch(REPO_LISTAR)
def test_montar_agrega_por_categoria(mock_listar):
    """Agrupe UUIDs e totais por GERAL/NNA/PCD."""
    pid = str(uuid.uuid4())
    uuid_geral = uuid.uuid4()
    uuid_nna = uuid.uuid4()
    uuid_pcd = uuid.uuid4()
    mock_listar.return_value = [
        {
            "processo_uuid": pid,
            "categoria_efetiva": "GERAL",
            "uuid": uuid_geral,
        },
        {
            "processo_uuid": pid,
            "categoria_efetiva": "NNA",
            "uuid": uuid_nna,
        },
        {
            "processo_uuid": pid,
            "categoria_efetiva": "PCD",
            "uuid": uuid_pcd,
        },
    ]

    resultado = HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga(
        [pid]
    )

    assert resultado[pid]["GERAL"] == {
        "total": 1,
        "candidatos_uuids": [str(uuid_geral)],
    }
    assert resultado[pid]["NNA"] == {
        "total": 1,
        "candidatos_uuids": [str(uuid_nna)],
    }
    assert resultado[pid]["PCD"] == {
        "total": 1,
        "candidatos_uuids": [str(uuid_pcd)],
    }


@patch(REPO_LISTAR)
def test_montar_categoria_nula_ou_invalida_vira_geral(mock_listar):
    """Categoria vazia ou desconhecida cai em GERAL."""
    pid = str(uuid.uuid4())
    uuid_nulo = uuid.uuid4()
    uuid_invalido = uuid.uuid4()
    mock_listar.return_value = [
        {
            "processo_uuid": pid,
            "categoria_efetiva": None,
            "uuid": uuid_nulo,
        },
        {
            "processo_uuid": pid,
            "categoria_efetiva": "OUTRA",
            "uuid": uuid_invalido,
        },
    ]

    resultado = HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga(
        [pid]
    )

    assert resultado[pid]["GERAL"]["total"] == 2
    assert set(resultado[pid]["GERAL"]["candidatos_uuids"]) == {
        str(uuid_nulo),
        str(uuid_invalido),
    }
    assert resultado[pid]["NNA"]["total"] == 0
    assert resultado[pid]["PCD"]["total"] == 0


@patch(REPO_LISTAR)
def test_montar_ignora_uuid_nulo(mock_listar):
    """Linhas sem uuid não entram na contagem."""
    pid = str(uuid.uuid4())
    mock_listar.return_value = [
        {
            "processo_uuid": pid,
            "categoria_efetiva": "GERAL",
            "uuid": None,
        }
    ]

    resultado = HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga(
        [pid]
    )

    assert resultado[pid]["GERAL"] == {
        "total": 0,
        "candidatos_uuids": [],
    }


@patch(REPO_LISTAR)
def test_montar_processo_extra_nas_rows_cria_bloco(mock_listar):
    """Processo presente só nas rows também é agregado."""
    pid_pedido = str(uuid.uuid4())
    pid_extra = str(uuid.uuid4())
    uuid_extra = uuid.uuid4()
    mock_listar.return_value = [
        {
            "processo_uuid": pid_extra,
            "categoria_efetiva": "NNA",
            "uuid": uuid_extra,
        }
    ]

    resultado = HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga(
        [pid_pedido]
    )

    assert pid_pedido in resultado
    assert resultado[pid_extra]["NNA"] == {
        "total": 1,
        "candidatos_uuids": [str(uuid_extra)],
    }
