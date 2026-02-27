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
