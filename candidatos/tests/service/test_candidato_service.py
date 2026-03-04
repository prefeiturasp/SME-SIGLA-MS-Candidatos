import pytest
from candidatos.service.candidato_service import remover_mascara_cpf, upsert_candidato_e_concurso
from candidatos.models import Candidato, ConcursoCandidato


pytestmark = pytest.mark.django_db


# --- remover_mascara_cpf (linhas 6-17) ---


def test_remover_mascara_cpf_vazio_retorna_vazio():
    assert remover_mascara_cpf('') == ''
    assert remover_mascara_cpf(None) == ''


def test_remover_mascara_cpf_remove_pontos_e_traco():
    assert remover_mascara_cpf('123.456.789-00') == '12345678900'
    assert remover_mascara_cpf('12345678900') == '12345678900'


def test_remover_mascara_cpf_aceita_nao_string():
    assert remover_mascara_cpf(12345678900) == '12345678900'


# --- upsert_candidato_e_concurso ---


def test_upsert_cria_candidato_e_concurso_quando_novo():
    data = {
        'nome': 'Fulano', 'cpf': '000.000.000-00', 'email': 'f@example.com',
        'data_nascimento': '01/01/1990', 'sexo': '1',
        'codigo_inscricao': '123',
        'pontos': 0,
    }
    candidato, concurso = upsert_candidato_e_concurso(data)

    assert Candidato.objects.count() == 1
    assert ConcursoCandidato.objects.count() == 1
    assert candidato.nome == 'Fulano'
    assert concurso.codigo_inscricao == '123'


def test_upsert_atualiza_candidato_existente_por_cpf():
    # cria inicialmente
    primeiro, _ = upsert_candidato_e_concurso({
        'nome': 'A', 'cpf': '111.111.111-11', 'email': 'a@example.com',
        'data_nascimento': '01/01/1990', 'sexo': '1',
        'codigo_inscricao': 'x',
        'pontos': 0,
    })
    # chama de novo com mesmo CPF e novos dados
    candidato, _c2 = upsert_candidato_e_concurso({
        'nome': 'B', 'cpf': '111.111.111-11', 'email': 'a2@example.com',
        'telefone': '9999', 'sexo': '2',
        'codigo_inscricao': 'y',
        'pontos': 0,
    })
    candidato.refresh_from_db()

    assert candidato.id == primeiro.id
    assert candidato.nome == 'B'
    assert candidato.telefone == '9999'


def test_upsert_data_nascimento_formato_invalido_nao_quebra():
    candidato, concurso = upsert_candidato_e_concurso({
        'cpf': '222.222.222-22', 'email': 'b@example.com', 'data_nascimento': '1990-31-12',
        'codigo_inscricao': '789',
        'pontos': 0,
    })
    # CPF é armazenado sem máscara pelo serviço
    assert Candidato.objects.filter(cpf='22222222222').exists()


def test_upsert_lookup_por_email_quando_sem_cpf():
    """Quando não há CPF no data, lookup é por email (linhas 35-36)."""
    candidato, c1 = upsert_candidato_e_concurso({
        'nome': 'X', 'email': 'unico@example.com', 'data_nascimento': '01/01/1990', 'sexo': '1',
        'codigo_inscricao': 'a', 'pontos': 0,
    })
    candidato2, c2 = upsert_candidato_e_concurso({
        'nome': 'Y', 'email': 'unico@example.com', 'codigo_inscricao': 'b', 'pontos': 0,
    })
    assert candidato.id == candidato2.id
    candidato2.refresh_from_db()
    assert candidato2.nome == 'Y'


def test_upsert_atualiza_data_nascimento_em_existente():
    """Atualização de candidato existente com data_nascimento (linha 75)."""
    upsert_candidato_e_concurso({
        'nome': 'A', 'cpf': '333.333.333-33', 'email': 'c@example.com',
        'data_nascimento': '01/01/1985', 'sexo': '1', 'codigo_inscricao': 'x', 'pontos': 0,
    })
    candidato, _ = upsert_candidato_e_concurso({
        'nome': 'A', 'cpf': '333.333.333-33', 'email': 'c@example.com',
        'data_nascimento': '15/06/1990', 'sexo': '1', 'codigo_inscricao': 'y', 'pontos': 0,
    })
    candidato.refresh_from_db()
    assert candidato.data_nascimento.year == 1990
    assert candidato.data_nascimento.month == 6
    assert candidato.data_nascimento.day == 15


def test_upsert_categoria_efetiva_pcd():
    """classificacao_deficiente preenchido define categoria_efetiva PCD (linhas 91-92)."""
    _, concurso = upsert_candidato_e_concurso({
        'cpf': '444.444.444-44', 'email': 'pcd@example.com', 'codigo_inscricao': 'p1',
        'classificacao_deficiente': 1, 'pontos': 0,
    })
    assert concurso.categoria_efetiva == 'PCD'
    assert concurso.classificacao_pcd == 1


def test_upsert_categoria_efetiva_nna():
    """classificacao_nna preenchido define categoria_efetiva NNA (linhas 93-94)."""
    _, concurso = upsert_candidato_e_concurso({
        'cpf': '555.555.555-55', 'email': 'nna@example.com', 'codigo_inscricao': 'n1',
        'classificacao_nna': 2, 'pontos': 0,
    })
    assert concurso.categoria_efetiva == 'NNA'
    assert concurso.classificacao_nna == 2


def test_upsert_none_if_empty_string_retorna_none():
    """classificacao_nna/classificacao_deficiente vazios resultam em None (linhas 84-86)."""
    _, concurso = upsert_candidato_e_concurso({
        'cpf': '666.666.666-66', 'email': 'vazio@example.com', 'codigo_inscricao': 'v1',
        'classificacao_nna': '', 'classificacao_deficiente': '', 'pontos': 0,
    })
    assert concurso.categoria_efetiva == 'GERAL'
    assert concurso.classificacao_nna is None
    assert concurso.classificacao_pcd is None
