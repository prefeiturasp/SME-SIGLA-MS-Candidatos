"""Módulo service/escolhas_api_service."""

import logging
from typing import Any

import requests
from candidatos.service.http_log import mascarar_headers
from django.conf import settings
from rest_framework import status
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class EscolhasApiService:
    """Service para comunicação com o microserviço de Escolhas."""

    DEFAULT_TIMEOUT = 60

    def __init__(self) -> None:
        """Inicializa URL base, headers e timeout do MS-Escolhas."""
        self.base_url = settings.ESCOLHAS_API_URL
        self.timeout_seconds = self.DEFAULT_TIMEOUT
        self.headers: dict[str, str] = {
            settings.API_KEY_HEADER: settings.ESCOLHAS_API_KEY,
        }

    def buscar_reconvocacoes(
        self, path: str = "/api/v1/escolhas/reconvocacao/"
    ) -> list[dict[str, Any]]:
        """Busca reconvocacoes.

        Args:
            path: Path.

        Returns:
            Lista com os registros obtidos.

        Raises:
            RequestException: Se a chamada HTTP falhar.
        """
        url = f"{self.base_url}{path}"
        logger.info(
            "Buscando reconvocações no microserviço de Escolhas | "
            f"method=GET url={url} "
            f"headers={mascarar_headers(self.headers)} "
            f"timeout_seconds={self.timeout_seconds}"
        )
        try:
            logger.info(
                f"Buscando reconvocações | url={url} "
                f"headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            response = http_client.get(
                url,
                timeout=self.timeout_seconds,
                headers=self.headers,
            )

        except requests.RequestException as exc:
            logger.exception(
                "Erro ao buscar reconvocações no microserviço de Escolhas | "
                f"erro={exc} headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            raise requests.RequestException(
                f"Erro ao buscar reconvocações no microserviço de Escolhas: {exc}"  # noqa: E501
            ) from exc

        if response.status_code == status.HTTP_200_OK:
            logger.info(
                "Reconvocações encontradas no microserviço de Escolhas | "
                f"method=GET url={url} status_code={response.status_code} "
                f"headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
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
                "Erro ao buscar reconvocações | "
                f"status_code={response.status_code} response={response.text} "
                f"headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            response.raise_for_status()
            return []

    def buscar_escolhas(
        self,
        concurso_uuid: str,
        path: str = "/api/v1/escolhas/?situacao__in=escolha,reconvocacao",
    ) -> list[dict[str, Any]]:
        """Busca escolhas.

        Args:
            concurso_uuid: UUID do concurso relacionado.
            path: Path.

        Returns:
            Lista com os registros obtidos.

        Raises:
            RequestException: Se a chamada HTTP falhar.
        """
        url = (
            f"{self.base_url}{path}&concurso_uuid={concurso_uuid}"
            f"&page_size=10000"
        )
        logger.info(
            f"Buscando escolhas | concurso_uuid={concurso_uuid} "
            f"path={path} url={url} "
            f"headers={mascarar_headers(self.headers)} "
            f"timeout_seconds={self.timeout_seconds}"
        )
        try:
            response = http_client.get(
                url,
                timeout=self.timeout_seconds,
                headers=self.headers,
            )
        except requests.RequestException as exc:
            logger.exception(
                "Erro ao buscar escolhas no microserviço de Escolhas | "
                f"erro={exc} headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            raise requests.RequestException(
                f"Erro ao buscar escolhas no microserviço de Escolhas: {exc}"  # noqa: E501
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
                "Erro ao buscar escolhas | "
                f"status_code={response.status_code} response={response.text} "
                f"headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            response.raise_for_status()
            return []
