"""Módulo service/agendas_api_service."""

import logging
from typing import Any

import requests
from candidatos.service.http_log import mascarar_headers
from django.conf import settings
from rest_framework import status
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class AgendasApiService:
    """Service para comunicação com o microserviço de Agendas."""

    DEFAULT_TIMEOUT = 10

    def __init__(self) -> None:
        """Inicializa URL base, headers e timeout do MS-Agendas."""
        self.base_url = settings.AGENDAS_API_URL
        self.timeout_seconds = self.DEFAULT_TIMEOUT
        self.headers: dict[str, str] = {
            settings.API_KEY_HEADER: settings.AGENDAS_API_KEY,
        }

    def remover_agendas_por_processo_uuid_e_cargo(
        self,
        processo_uuid: str,
        codigo_cargo: str,
        path: str = "/api/v1/agendas/por-processo-e-cargo/",
    ) -> dict[str, Any]:
        """Remove agendas por processo e cargo no MS-Agendas.

        Args:
            processo_uuid: UUID do processo de convocação.
            codigo_cargo: UUID do cargo vinculado à agenda.
            path: Path do endpoint de exclusão.

        Returns:
            Resposta JSON do MS-Agendas (ex.: ``{"excluidas": N}``).

        Raises:
            RequestException: Se a chamada HTTP falhar.
        """
        url = f"{self.base_url}{path}"
        parametros = {
            "processo_uuid": processo_uuid,
            "cargo": codigo_cargo,
        }
        logger.info(
            "Removendo agendas por processo e cargo no MS-Agendas | "
            f"method=DELETE url={url} params={parametros} "
            f"processo_uuid={processo_uuid} codigo_cargo={codigo_cargo} "
            f"headers={mascarar_headers(self.headers)} "
            f"timeout_seconds={self.timeout_seconds}"
        )
        try:
            response = http_client.delete(
                url,
                headers=self.headers,
                params=parametros,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            logger.exception(
                "Erro ao conectar com o microserviço de Agendas | "
                f"erro={exc} headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            raise requests.RequestException(
                f"Erro ao conectar com o microserviço de Agendas: {exc}"
            ) from exc

        if response.status_code == status.HTTP_200_OK:
            corpo_resposta = response.json() if response.content else {}
            logger.info(
                "Agendas removidas por processo e cargo no MS-Agendas | "
                f"method=DELETE url={url} params={parametros} "
                f"status_code={response.status_code} "
                f"response={corpo_resposta} "
                f"headers={mascarar_headers(self.headers)} "
                f"timeout_seconds={self.timeout_seconds}"
            )
            return corpo_resposta

        logger.error(
            "Erro ao remover agendas por processo e cargo | "
            f"status_code={response.status_code} response={response.text} "
            f"headers={mascarar_headers(self.headers)} "
            f"timeout_seconds={self.timeout_seconds}"
        )
        response.raise_for_status()
        return {}
