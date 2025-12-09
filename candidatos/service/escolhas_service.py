import logging
import requests
from typing import List, Dict, Any
from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)


class EscolhasService:
    """
    Service para comunicação com o microserviço de Escolhas.
    """
    DEFAULT_TIMEOUT = 10

    @classmethod
    def _get_base_url(cls) -> str:
        """
        Obtém a URL base do microserviço de Escolhas a partir das configurações.
        """
        base_url = getattr(settings, 'ESCOLHAS_API_URL', None)
        if not base_url:
            raise ValueError('ESCOLHAS_API_URL não configurada no settings')
        return base_url.rstrip('/')

    @classmethod
    def buscar_reconvocacoes(cls, path: str = '/api/v1/escolhas/reconvocacao/') -> List[Dict[str, Any]]:
        """
        Busca escolhas com situação de reconvocação.
        
        Args:
            path: Caminho do endpoint (padrão: /api/v1/escolhas/reconvocacao)
            
        Returns:
            Lista de dicionários com 'uuid' e 'candidato_uuid'
            
        Raises:
            requests.RequestException: Em caso de erro na requisição
            ValueError: Se a URL não estiver configurada
        """
        base_url = cls._get_base_url()
        url = f"{base_url}{path}"
        
        try:
            logger.info(f"Buscando reconvocações em: {url}")
            response = requests.get(url, timeout=cls.DEFAULT_TIMEOUT)
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                # Garante que retorna uma lista
                if isinstance(data, list):
                    return data
                # Se for um dicionário com 'results', retorna os results
                if isinstance(data, dict) and 'results' in data:
                    return data['results']
                # Se for um dicionário direto, retorna como lista
                if isinstance(data, dict):
                    return [data]
                return []
            else:
                logger.error(f"Erro ao buscar reconvocações: {response.status_code} - {response.text}")
                response.raise_for_status()
                return []
                
        except requests.RequestException as exc:
            logger.exception(f"Erro ao conectar com o microserviço de Escolhas: {exc}")
            raise requests.RequestException(f"Erro ao conectar com o microserviço de Escolhas: {exc}") from exc

