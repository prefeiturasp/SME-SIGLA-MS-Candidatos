"""Testes unitários para candidatos/service/eliminacao_service.py.

Cobre aplicar_eliminacao (linhas 12-25).
"""
from __future__ import annotations
from typing import Any
from uuid import uuid4
import pytest
from django.utils import timezone
from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatoEliminacao, ConcursoCandidatosLote
from candidatos.service.eliminacao_service import aplicar_eliminacao
pytestmark = pytest.mark.django_db

def _candidato(**kwargs: Any) -> Any:
    """Executa  candidato.
    
    Args:
        **kwargs: Argumentos nomeados variáveis.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return Candidato.objects.create(nome=kwargs.get('nome', 'Teste'), cpf=kwargs.get('cpf', f'{uuid4().int % 10 ** 11:011d}'), email=kwargs.get('email', f'{uuid4().hex[:8]}@example.com'), telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')

@pytest.fixture
def lote() -> Any:
    """Executa lote.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso Teste')

@pytest.fixture
def cc_habilitado(lote: Any) -> Any:
    """Executa cc habilitado.
    
    Args:
        lote: Parâmetro lote da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return ConcursoCandidato.objects.create(candidato=_candidato(), lote=lote, codigo_inscricao='001', eliminado=False)

def test_aplicar_eliminacao_marca_eliminado_e_cria_historico(cc_habilitado: Any) -> None:
    """Verifica aplicar eliminacao marca eliminado e cria historico.
    
    Args:
        cc_habilitado: Parâmetro cc habilitado da operação.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc, hist = aplicar_eliminacao(candidato_uuid=cc_habilitado.uuid, motivo='Desistência', executado_por='sistema')
    cc.refresh_from_db()
    assert cc.eliminado is True
    assert cc.eliminado_motivo == 'Desistência'
    assert cc.eliminado_por == 'sistema'
    assert cc.eliminado_em is not None
    assert hist.concurso_candidato_id == cc.id
    assert hist.motivo == 'Desistência'
    assert hist.executado_por == 'sistema'
    assert ConcursoCandidatoEliminacao.objects.filter(concurso_candidato=cc).count() == 1

def test_aplicar_eliminacao_motivo_e_executado_vazios(cc_habilitado: Any) -> None:
    """Verifica aplicar eliminacao motivo e executado vazios.
    
    Args:
        cc_habilitado: Parâmetro cc habilitado da operação.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc, hist = aplicar_eliminacao(candidato_uuid=cc_habilitado.uuid, motivo='', executado_por='')
    cc.refresh_from_db()
    assert cc.eliminado_motivo == ''
    assert cc.eliminado_por == ''
    assert hist.motivo == ''
    assert hist.executado_por == ''

def test_aplicar_eliminacao_ja_eliminado_levanta_value_error(lote: Any) -> None:
    """Verifica aplicar eliminacao ja eliminado levanta value error.
    
    Args:
        lote: Parâmetro lote da operação.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = ConcursoCandidato.objects.create(candidato=_candidato(), lote=lote, codigo_inscricao='002', eliminado=True)
    with pytest.raises(ValueError, match='já está eliminado'):
        aplicar_eliminacao(candidato_uuid=cc.uuid, motivo='', executado_por='')

def test_aplicar_eliminacao_uuid_inexistente_levanta_does_not_exist() -> None:
    """Verifica aplicar eliminacao uuid inexistente levanta does not exist.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    with pytest.raises(ConcursoCandidato.DoesNotExist):
        aplicar_eliminacao(candidato_uuid=uuid4(), motivo='', executado_por='')

def _make_candidato(cpf: Any='00000000001', email: Any='c1@test.com') -> Any:
    """Executa  make candidato.
    
    Args:
        cpf: Parâmetro cpf da operação.
        email: Parâmetro email da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return Candidato.objects.create(nome='Candidato Teste', cpf=cpf, email=email, data_nascimento='1990-01-01')

def _make_cc(candidato: Any=None, **kwargs: Any) -> Any:
    """Executa  make cc.
    
    Args:
        candidato: Parâmetro candidato da operação.
        **kwargs: Argumentos nomeados variáveis.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    if candidato is None:
        candidato = _make_candidato()
    return ConcursoCandidato.objects.create(candidato=candidato, codigo_inscricao='INS-001', classificacao=1, **kwargs)

def test_aplicar_eliminacao_marca_eliminado() -> None:
    """Verifica aplicar eliminacao marca eliminado.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = _make_cc()
    assert cc.eliminado is False
    cc_ret, hist = aplicar_eliminacao(candidato_uuid=cc.uuid, motivo='Falta de documentos', executado_por='admin')
    cc.refresh_from_db()
    assert cc.eliminado is True
    assert cc.eliminado_motivo == 'Falta de documentos'
    assert cc.eliminado_por == 'admin'
    assert cc.eliminado_em is not None

def test_aplicar_eliminacao_cria_historico() -> None:
    """Verifica aplicar eliminacao cria historico.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = _make_cc()
    cc_ret, hist = aplicar_eliminacao(candidato_uuid=cc.uuid, motivo='Reprovado', executado_por='gestor')
    assert ConcursoCandidatoEliminacao.objects.filter(concurso_candidato=cc).count() == 1
    assert hist.motivo == 'Reprovado'
    assert hist.executado_por == 'gestor'
    assert hist.concurso_candidato_id == cc.id

def test_aplicar_eliminacao_retorna_tupla_correta() -> None:
    """Verifica aplicar eliminacao retorna tupla correta.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = _make_cc()
    result = aplicar_eliminacao(candidato_uuid=cc.uuid)
    assert isinstance(result, tuple)
    assert len(result) == 2
    cc_ret, hist = result
    assert cc_ret.id == cc.id
    assert isinstance(hist, ConcursoCandidatoEliminacao)

def test_aplicar_eliminacao_sem_motivo_usa_string_vazia() -> None:
    """Verifica aplicar eliminacao sem motivo usa string vazia.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = _make_cc()
    cc_ret, hist = aplicar_eliminacao(candidato_uuid=cc.uuid)
    cc.refresh_from_db()
    assert cc.eliminado_motivo == ''
    assert cc.eliminado_por == ''
    assert hist.motivo == ''
    assert hist.executado_por == ''

def test_aplicar_eliminacao_atualiza_eliminado_em() -> None:
    """Verifica aplicar eliminacao atualiza eliminado em.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    before = timezone.now()
    cc = _make_cc()
    aplicar_eliminacao(candidato_uuid=cc.uuid)
    cc.refresh_from_db()
    assert cc.eliminado_em >= before

def test_aplicar_eliminacao_ja_eliminado_levanta_erro() -> None:
    """Verifica aplicar eliminacao ja eliminado levanta erro.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = _make_cc()
    aplicar_eliminacao(candidato_uuid=cc.uuid, motivo='Primeira vez')
    with pytest.raises(ValueError, match='já está eliminado'):
        aplicar_eliminacao(candidato_uuid=cc.uuid, motivo='Segunda vez')

def test_aplicar_eliminacao_ja_eliminado_nao_cria_segundo_historico() -> None:
    """Verifica aplicar eliminacao ja eliminado nao cria segundo historico.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cc = _make_cc()
    aplicar_eliminacao(candidato_uuid=cc.uuid)
    with pytest.raises(ValueError):
        aplicar_eliminacao(candidato_uuid=cc.uuid)
    assert ConcursoCandidatoEliminacao.objects.filter(concurso_candidato=cc).count() == 1

def test_aplicar_eliminacao_uuid_inexistente() -> None:
    """Verifica aplicar eliminacao uuid inexistente.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    import uuid as _uuid
    with pytest.raises(ConcursoCandidato.DoesNotExist):
        aplicar_eliminacao(candidato_uuid=_uuid.uuid4())

def test_aplicar_eliminacao_atomicidade(monkeypatch: Any) -> None:
    """Se a criação do histórico falhar, o ConcursoCandidato não deve ficar.
    
    Args:
        monkeypatch: Fixture do pytest para substituir objetos.
    
    Returns:
        Não retorna valor.
    
    Raises:
        RuntimeError: Se ocorrer erro nesta operação.
    """
    cc = _make_cc()

    def create_raise(*args: Any, **kwargs: Any) -> None:
        """Executa create raise.
        
        Args:
            *args: Argumentos posicionais variáveis.
            **kwargs: Argumentos nomeados variáveis.
        
        Returns:
            Não retorna valor.
        
        Raises:
            RuntimeError: Se ocorrer erro nesta operação.
        """
        raise RuntimeError('Falha simulada')
    monkeypatch.setattr(ConcursoCandidatoEliminacao.objects, 'create', create_raise)
    with pytest.raises(RuntimeError):
        aplicar_eliminacao(candidato_uuid=cc.uuid)
    cc.refresh_from_db()
    assert cc.eliminado is False
