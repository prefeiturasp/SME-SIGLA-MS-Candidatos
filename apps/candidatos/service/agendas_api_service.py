"""Módulo service/agendas_api_service."""

import logging
from typing import Any

import requests
from django.conf import settings
from rest_framework import status
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class AgendasApiService:
    """Service para comunicação com o microserviço de Agendas."""

    DEFAULT_TIMEOUT = 10

    @classmethod
    def remover_agendas_por_processo_uuid_e_cargo(
        cls,
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
        base_url = settings.AGENDAS_API_URL
        url = f"{base_url}{path}"
        headers = {
            settings.API_KEY_HEADER: settings.AGENDAS_API_KEY,
        }
        parametros = {
            "processo_uuid": processo_uuid,
            "cargo": codigo_cargo,
        }
        logger.info(
            f"Removendo agendas por processo e cargo no MS-Agendas | "
            f"method=DELETE url={url} params={parametros} "
            f"processo_uuid={processo_uuid} codigo_cargo={codigo_cargo}"
        )
        try:
            response = http_client.delete(
                url,
                headers=headers,
                params=parametros,
                timeout=cls.DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.exception(
                f"Erro ao conectar com o microserviço de Agendas | erro={exc}"
            )
            raise requests.RequestException(
                f"Erro ao conectar com o microserviço de Agendas: {exc}"
            ) from exc

        if response.status_code == status.HTTP_200_OK:
            corpo_resposta = response.json() if response.content else {}
            logger.info(
                f"Agendas removidas por processo e cargo no MS-Agendas | "
                f"method=DELETE url={url} params={parametros} "
                f"status_code={response.status_code} "
                f"response={corpo_resposta}"
            )
            return corpo_resposta

        logger.error(
            f"Erro ao remover agendas por processo e cargo | "
            f"status_code={response.status_code} response={response.text}"
        )
        response.raise_for_status()
        return {}
