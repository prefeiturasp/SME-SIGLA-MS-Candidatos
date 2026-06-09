"""Módulo service/escolhas_service."""
import logging
from typing import Any

import requests
from django.conf import settings
from rest_framework import status
from sigla_sdk.context import get_correlation_id
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class EscolhasService:
    """Service para comunicação com o microserviço de Escolhas."""

    DEFAULT_TIMEOUT = 10

    @classmethod
    def _get_base_url(cls) -> str:
        """Obtém a URL base do microserviço de Escolhas a partir das.

        configurações.
        """
        base_url = getattr(settings, "ESCOLHAS_API_URL", None)
        if not base_url:
            raise ValueError("ESCOLHAS_API_URL não configurada no settings")
        return base_url.rstrip("/")  # type: ignore[no-any-return]

    @classmethod
    def buscar_reconvocacoes(
        cls, path: str = "/api/v1/escolhas/reconvocacao/"
    ) -> list[dict[str, Any]]:
        """Busca escolhas com situação de reconvocação.

        Args:
            path: Caminho do endpoint (padrão: /api/v1/escolhas/reconvocacao)

        Returns:
            Lista de dicionários com 'uuid' e 'candidato_uuid'
        Raises:
            requests.RequestException: Em caso de erro na requisição
            ValueError: Se a URL não estiver configurada.
        """
        base_url = cls._get_base_url()
        url = f"{base_url}{path}"
        logger.info(
            "Buscando reconvocações no microserviço de Escolhas",
            extra={
                "method": "GET",
                "correlation_id": get_correlation_id(),
                "url": url,
            },
        )
        try:
            logger.info(f"Buscando reconvocações em: {url}")
            response = http_client.get(url, timeout=cls.DEFAULT_TIMEOUT)

        except requests.RequestException as exc:
            logger.exception(
                f"Erro ao conectar com o microserviço de Escolhas: {exc}"
            )
            raise requests.RequestException(
                f"Erro ao conectar com o microserviço de Escolhas: {exc}"
            ) from exc

        if response.status_code == status.HTTP_200_OK:
            logger.info(
                "Reconvocações encontradas no microserviço de Escolhas",
                extra={
                    "method": "GET",
                    "correlation_id": get_correlation_id(),
                    "url": url,
                    "status_code": response.status_code,
                },
            )
            data = response.json()
            # Garante que retorna uma lista
            if isinstance(data, list):
                return data
            # Se for um dicionário com 'results', retorna os results
            if isinstance(data, dict) and "results" in data:
                return data["results"]  # type: ignore[no-any-return]
            # Se for um dicionário direto, retorna como lista
            if isinstance(data, dict):
                return [data]
            return []
        else:
            logger.error(
                f"Erro ao buscar reconvocações: {response.status_code} - {response.text}"  # noqa: E501
            )
            response.raise_for_status()
            return []

    @classmethod
    def buscar_escolhas(
        cls,
        concurso_uuid: str,
        path: str = "/api/v1/escolhas/?situacao__in=escolha,reconvocacao",
    ) -> list[dict[str, Any]]:
        """Busca escolhas com situação de escolha ou reconvocação.

        Args:
            concurso_uuid: UUID do concurso
            path: Caminho do endpoint (padrão:
            /api/v1/escolhas/?situacao=escolha,reconvocacao)

        Returns:
            Lista de dicionários com 'uuid' e 'candidato_uuid'
        Raises:
            requests.RequestException: Em caso de erro na requisição
            ValueError: Se a URL não estiver configurada.
        """
        base_url = cls._get_base_url()
        url = f"{base_url}{path}&concurso_uuid={concurso_uuid}&page_size=10000"
        logger.info(
            "Buscando escolhas",
            extra={
                "correlation_id": get_correlation_id(),
                "concurso_uuid": concurso_uuid,
                "path": path,
                "url": url,
            },
        )
        try:
            response = http_client.get(url, timeout=cls.DEFAULT_TIMEOUT)
        except requests.RequestException as exc:
            logger.exception(f"Erro ao buscar escolhas: {exc}")
            raise requests.RequestException(
                f"Erro ao buscar escolhas: {exc}"
            ) from exc

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # Garante que retorna uma lista
            if isinstance(data, list):
                return data
            # Se for um dicionário com 'results', retorna os results
            if isinstance(data, dict) and "results" in data:
                return data["results"]  # type: ignore[no-any-return]
            # Se for um dicionário direto, retorna como lista
            if isinstance(data, dict):
                return [data]
            return []
        else:
            logger.error(
                f"Erro ao buscar escolhas: {response.status_code} - {response.text}"  # noqa: E501
            )
            response.raise_for_status()
            return []
