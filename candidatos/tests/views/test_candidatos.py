import pytest
from django.urls import reverse
from rest_framework import status
from candidatos.models import Candidato, ConcursoCandidatosLote, ConcursoCandidato


pytestmark = pytest.mark.django_db


@pytest.fixture
def candidato_url():
    return reverse('candidato-list')


def test_list_candidatos(api_client, candidatos_criados, candidato_url):
    response = api_client.get(candidato_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3


def test_create_candidatos_em_lote(api_client, candidato_url):
    payload = {
        'concurso_uuid': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'concurso_nome': 'Concurso X',
        'candidatos': [
            {
                'nome': 'Ana Costa', 'cpf': '555.666.777-88', 'email': 'ana.costa@email.com',
                'telefone': '(11) 66666-6666', 'data_nascimento': '25/08/1988', 'genero': 'F',
                'endereco': 'Rua Augusta, 321', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01305-000',
                'status': 'ativo', 'observacao': 'Nova candidata', 'codigo_inscricao': '12345',
                'classificacao': '10', 'pontos': '95',
            }
        ]
    }

    response = api_client.post(candidato_url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['total_itens'] == 1
    assert ConcursoCandidatosLote.objects.count() == 1
    lote = ConcursoCandidatosLote.objects.first()
    assert ConcursoCandidato.objects.filter(lote=lote).count() == 1
    # CPF é armazenado sem máscara pelo serviço
    assert Candidato.objects.filter(cpf='55566677788').exists()


def test_retrieve_candidato(api_client, candidatos_criados):
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'João Silva'


def test_update_candidato(api_client, candidatos_criados):
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    dados_atualizados = {
        'nome': 'João Silva Santos', 'cpf': '123.456.789-00', 'email': 'joao.silva.santos@email.com',
        'telefone': '(11) 99999-9999', 'data_nascimento': '1990-01-15', 'genero': 'M', 'endereco': 'Rua das Flores, 123',
        'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01234-567', 'status': 'ativo', 'observacoes': 'Candidato atualizado'
    }
    response = api_client.put(url, dados_atualizados, format='json')
    assert response.status_code == status.HTTP_200_OK


def test_partial_update_candidato(api_client, candidatos_criados):
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    response = api_client.patch(url, {'telefone': '(11) 11111-1111', 'status': 'suspenso'}, format='json')
    assert response.status_code == status.HTTP_200_OK


def test_delete_candidato(api_client, candidatos_criados):
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


# --- Testes da action buscar (feature/143715-consulta-concursado) ---


@pytest.fixture
def candidato_com_concurso():
    """Candidato com registro em ConcursoCandidato para testar a busca."""
    from candidatos.models import ConcursoCandidatosLote
    from uuid import uuid4
    candidato = Candidato.objects.create(
        nome='Carlos Concursado',
        cpf='444.555.666-77',
        email='carlos.concursado@email.com',
        rg='12.345.678-9',
        registro_funcional='RF001',
        telefone='',
        data_nascimento='1988-03-10',
        genero='M',
        endereco='',
        cidade='São Paulo',
        estado='SP',
        cep='',
        status='ativo',
        observacoes='',
    )
    lote = ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome='Concurso Teste 143715',
    )
    ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote,
        codigo_inscricao='INS001',
        classificacao=1,
    )
    return {'candidato': candidato, 'lote': lote}


def test_buscar_sem_parametros_retorna_400(api_client):
    """Buscar sem nome, cpf, rg ou registro_funcional deve retornar 400."""
    url = reverse('candidato-buscar')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'nome' in response.data['detail'] or 'cpf' in response.data['detail']


def test_buscar_por_nome_retorna_candidatos_com_concursos(api_client, candidato_com_concurso):
    """Buscar por nome deve retornar candidatos com lista de concursos."""
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'nome': 'Carlos'})
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) >= 1
    item = next((x for x in response.data if x.get('nome') == 'Carlos Concursado'), None)
    assert item is not None
    assert 'concursos' in item
    assert len(item['concursos']) >= 1
    assert item['concursos'][0].get('concurso_nome') == 'Concurso Teste 143715'
    assert 'concurso_uuid' in item['concursos'][0]
    assert 'concurso_candidato_uuid' in item['concursos'][0]


def test_buscar_por_cpf_retorna_candidatos_com_concursos(api_client, candidato_com_concurso):
    """Buscar por CPF (parcial) deve retornar candidatos com concursos."""
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'cpf': '444.555'})
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    item = next((x for x in response.data if '444.555.666' in x.get('cpf', '')), None)
    assert item is not None
    assert 'concursos' in item


def test_buscar_por_rg_retorna_candidatos_com_concursos(api_client, candidato_com_concurso):
    """Buscar por RG deve retornar candidatos com concursos."""
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'rg': '12.345'})
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    item = next((x for x in response.data if x.get('nome') == 'Carlos Concursado'), None)
    assert item is not None
    assert 'concursos' in item


def test_buscar_por_registro_funcional_retorna_candidatos_com_concursos(api_client, candidato_com_concurso):
    """Buscar por registro funcional deve retornar candidatos com concursos."""
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'registro_funcional': 'RF001'})
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    item = next((x for x in response.data if x.get('nome') == 'Carlos Concursado'), None)
    assert item is not None
    assert 'concursos' in item


def test_buscar_retorna_campos_concurso_uuid_nome_candidato_uuid(api_client, candidato_com_concurso):
    """Resposta da busca deve incluir concurso_uuid, concurso_nome e concurso_candidato_uuid nos concursos."""
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'nome': 'Carlos'})
    assert response.status_code == status.HTTP_200_OK
    item = next((x for x in response.data if x.get('nome') == 'Carlos Concursado'), None)
    assert item is not None
    concurso_data = item['concursos'][0]
    assert 'concurso_uuid' in concurso_data
    assert 'concurso_nome' in concurso_data
    assert concurso_data['concurso_nome'] == 'Concurso Teste 143715'
    assert 'concurso_candidato_uuid' in concurso_data


def test_buscar_agrupa_por_candidato_com_multiplos_concursos(api_client, candidato_com_concurso):
    """Um mesmo candidato em mais de um concurso deve aparecer uma vez com lista de concursos."""
    from candidatos.models import ConcursoCandidatosLote
    from uuid import uuid4
    candidato = candidato_com_concurso['candidato']
    lote2 = ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome='Outro Concurso',
    )
    ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote2,
        codigo_inscricao='INS002',
        classificacao=2,
    )
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'cpf': candidato.cpf})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert len(response.data[0]['concursos']) == 2


def test_buscar_retorna_lista_vazia_quando_nao_encontra(api_client):
    """Buscar com termo que não existe deve retornar lista vazia."""
    url = reverse('candidato-buscar')
    response = api_client.get(url, {'nome': 'NomeQueNaoExisteXYZ123'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
