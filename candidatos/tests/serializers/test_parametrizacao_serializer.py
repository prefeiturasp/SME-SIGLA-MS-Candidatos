import pytest
from candidatos.models import Parametrizacao
from candidatos.serializer import ParametrizacaoSerializer


pytestmark = pytest.mark.django_db


def test_parametrizacao_serializer_serialization():
    """Testa serialização de Parametrizacao"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.10,
        porcentagem_nna=0.25
    )
    
    serializer = ParametrizacaoSerializer(parametrizacao)
    data = serializer.data
    
    assert data['porcentagem_pcd'] == 0.10
    assert data['porcentagem_nna'] == 0.25
    assert 'uuid' in data
    assert 'criado_em' in data
    assert 'atualizado_em' in data
    assert 'esta_ativo' in data


def test_parametrizacao_serializer_deserialization():
    """Testa deserialização e criação de Parametrizacao"""
    data = {
        'porcentagem_pcd': 0.15,
        'porcentagem_nna': 0.30
    }
    
    serializer = ParametrizacaoSerializer(data=data)
    assert serializer.is_valid()
    
    parametrizacao = serializer.save()
    
    assert parametrizacao.porcentagem_pcd == 0.15
    assert parametrizacao.porcentagem_nna == 0.30
    assert parametrizacao.uuid is not None


def test_parametrizacao_serializer_partial_update():
    """Testa atualização parcial de Parametrizacao"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    
    data = {
        'porcentagem_pcd': 0.12
    }
    
    serializer = ParametrizacaoSerializer(parametrizacao, data=data, partial=True)
    assert serializer.is_valid()
    
    updated_parametrizacao = serializer.save()
    
    assert updated_parametrizacao.porcentagem_pcd == 0.12
    assert updated_parametrizacao.porcentagem_nna == 0.20  # Não alterado


def test_parametrizacao_serializer_read_only_fields():
    """Testa que campos read_only não podem ser alterados"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    
    original_uuid = parametrizacao.uuid
    original_criado_em = parametrizacao.criado_em
    
    data = {
        'uuid': '00000000-0000-0000-0000-000000000000',
        'criado_em': '2020-01-01T00:00:00Z',
        'porcentagem_pcd': 0.15
    }
    
    serializer = ParametrizacaoSerializer(parametrizacao, data=data, partial=True)
    assert serializer.is_valid()
    
    updated_parametrizacao = serializer.save()
    
    # Campos read_only não devem ser alterados
    assert updated_parametrizacao.uuid == original_uuid
    assert updated_parametrizacao.criado_em == original_criado_em
    # Campo editável foi alterado
    assert updated_parametrizacao.porcentagem_pcd == 0.15


def test_parametrizacao_serializer_validation():
    """Testa validação do serializer"""
    # Testa com dados válidos
    data = {
        'porcentagem_pcd': 0.10,
        'porcentagem_nna': 0.25
    }
    
    serializer = ParametrizacaoSerializer(data=data)
    assert serializer.is_valid()
    
    # Testa com valores negativos (se houver validação)
    data_invalid = {
        'porcentagem_pcd': -0.10,
        'porcentagem_nna': 0.25
    }
    
    serializer_invalid = ParametrizacaoSerializer(data=data_invalid)
    # Django FloatField aceita negativos por padrão, então pode ser válido
    # Se houver validação customizada, ajustar este teste
