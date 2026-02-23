import pytest
from candidatos.service.candidato_service import upsert_candidato_e_concurso
from candidatos.models import Candidato, ConcursoCandidato


pytestmark = pytest.mark.django_db


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
    assert Candidato.objects.filter(cpf='22222222222').exists()
