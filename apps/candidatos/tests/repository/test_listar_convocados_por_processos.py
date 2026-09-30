"""Testes de ConcursoCandidatoRepository.listar_convocados_por_processos."""

from __future__ import annotations

from uuid import uuid4

import pytest
from candidatos.models import Candidato, ConcursoCandidato
from candidatos.repository import ConcursoCandidatoRepository

pytestmark = pytest.mark.django_db


def _candidato(**kwargs):
    """Candidato de exemplo para os testes."""
    return Candidato.objects.create(
        nome=kwargs.get("nome", "Teste"),
        cpf=kwargs.get("cpf", f"{uuid4().int % 10**11:011d}"),
        email=kwargs.get("email", f"{uuid4().hex[:8]}@example.com"),
        telefone="",
        data_nascimento="1990-01-01",
        genero="M",
        endereco="",
        cidade="",
        estado="",
        cep="",
        status="ativo",
        observacoes="",
    )


def _cc(**kwargs):
    """ConcursoCandidato de exemplo para os testes."""
    return ConcursoCandidato.objects.create(
        candidato=kwargs.get("candidato") or _candidato(),
        concurso_uuid=kwargs.get("concurso_uuid", uuid4()),
        concurso_nome="Concurso Teste",
        codigo_inscricao=kwargs.get("codigo_inscricao", uuid4().hex[:8]),
        codigo_cargo=kwargs.get("codigo_cargo", "CARGO1"),
        foi_convocado=kwargs.get("foi_convocado", True),
        processo_uuid=kwargs.get("processo_uuid"),
        categoria_efetiva=kwargs.get("categoria_efetiva", "GERAL"),
    )


def test_listar_convocados_por_processos_lista_vazia():
    """Sem processo_uuids, retorna lista vazia sem consultar."""
    assert (
        ConcursoCandidatoRepository.listar_convocados_por_processos([]) == []
    )


def test_listar_convocados_por_processos_filtra_convocados():
    """Retorna apenas convocados do processo informado."""
    processo = uuid4()
    outro = uuid4()

    cc_ok = _cc(processo_uuid=processo, categoria_efetiva="NNA")
    _cc(processo_uuid=outro, categoria_efetiva="GERAL")
    _cc(processo_uuid=processo, foi_convocado=False)

    rows = ConcursoCandidatoRepository.listar_convocados_por_processos(
        [processo]
    )

    assert len(rows) == 1
    assert rows[0]["processo_uuid"] == processo
    assert rows[0]["categoria_efetiva"] == "NNA"
    assert rows[0]["uuid"] == cc_ok.uuid


def test_listar_convocados_por_processos_varios_processos():
    """Busca convocados de múltiplos processos."""
    p1 = uuid4()
    p2 = uuid4()
    _cc(processo_uuid=p1, categoria_efetiva="GERAL")
    _cc(processo_uuid=p2, categoria_efetiva="PCD")

    rows = ConcursoCandidatoRepository.listar_convocados_por_processos(
        [p1, p2]
    )

    assert len(rows) == 2
    processos = {row["processo_uuid"] for row in rows}
    assert processos == {p1, p2}
