"""Módulo tests/service/test_lotes_service."""
from __future__ import annotations
from typing import Any
import uuid
import pytest
from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote
from candidatos.service.lotes_service import SalvarLotesException, salvar_lotes
pytestmark = pytest.mark.django_db

def _criar_candidato(nome: str, cpf: str, email: str) -> Candidato:
    """Executa  criar candidato."""
    return Candidato.objects.create(nome=nome, cpf=cpf, email=email)

def _criar_concurso_candidato(lote: ConcursoCandidatosLote, candidato: Candidato, codigo_inscricao: str) -> ConcursoCandidato:
    """Executa  criar concurso candidato."""
    return ConcursoCandidato.objects.create(lote=lote, candidato=candidato, codigo_inscricao=codigo_inscricao)

def test_salvar_lotes_persiste_chave_inscrito_quando_informada() -> None:
    """Verifica salvar lotes persiste chave inscrito quando informada."""
    concurso_uuid = str(uuid.uuid4())
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Concurso Teste')
    candidato = _criar_candidato('Alice', '111.111.111-11', 'alice@example.com')
    cc = _criar_concurso_candidato(lote=lote, candidato=candidato, codigo_inscricao='INSC001')
    total = salvar_lotes(concurso_uuid=concurso_uuid, lotes=[{'lote': 123, 'empresa': 1, 'vaga': 10, 'identificacao': 'INSC001', 'chave_inscrito': 'CHV-123', 'numfunc': 'RF001', 'numvinc': 'V001'}])
    cc.refresh_from_db()
    assert total == 1
    assert cc.chave_inscrito == 'CHV-123'

def test_salvar_lotes_define_chave_inscrito_como_none_quando_nao_informada() -> None:
    """Verifica salvar lotes define chave inscrito como none quando nao informada."""
    concurso_uuid = str(uuid.uuid4())
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Concurso Teste')
    candidato = _criar_candidato('Bruno', '222.222.222-22', 'bruno@example.com')
    cc = _criar_concurso_candidato(lote=lote, candidato=candidato, codigo_inscricao='INSC002')
    total = salvar_lotes(concurso_uuid=concurso_uuid, lotes=[{'lote': 124, 'empresa': 1, 'vaga': 11, 'identificacao': 'INSC002', 'numfunc': 'RF002', 'numvinc': 'V002'}])
    cc.refresh_from_db()
    assert total == 1
    assert cc.chave_inscrito is None

def test_salvar_lotes_faz_rollback_total_quando_ha_erro() -> None:
    """Verifica salvar lotes faz rollback total quando ha erro."""
    concurso_uuid = str(uuid.uuid4())
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Concurso Teste')
    candidato = _criar_candidato('Carla', '333.333.333-33', 'carla@example.com')
    cc = _criar_concurso_candidato(lote=lote, candidato=candidato, codigo_inscricao='INSC003')
    cc.numero_lote = 125
    cc.codigo_sigpec = 9
    cc.numero_vaga = 99
    cc.chave_inscrito = 'CHV-OLD'
    cc.save(update_fields=['numero_lote', 'codigo_sigpec', 'numero_vaga', 'chave_inscrito'])
    with pytest.raises(SalvarLotesException):
        salvar_lotes(concurso_uuid=concurso_uuid, lotes=[{'lote': 125, 'empresa': 1, 'vaga': 12, 'identificacao': 'INSC003', 'chave_inscrito': 'CHV-NEW', 'numfunc': 'RF003', 'numvinc': 'V003'}, {'lote': 125, 'empresa': 1, 'vaga': 13, 'identificacao': 'INSC999', 'chave_inscrito': 'CHV-ERR', 'numfunc': 'RF004', 'numvinc': 'V004'}])
    cc.refresh_from_db()
    assert cc.numero_lote == 125
    assert cc.codigo_sigpec == 9
    assert cc.numero_vaga == 99
    assert cc.chave_inscrito == 'CHV-OLD'
