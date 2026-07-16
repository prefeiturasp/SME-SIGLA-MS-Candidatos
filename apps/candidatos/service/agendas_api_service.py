"""Módulo service/agendas_api_service."""

import logging
from typing import Any

import requests
from django.conf import settings
from rest_framework import status
from sigla_sdk.context import get_correlation_id
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class AgendasApiService:
    """Service para comunicação com o microserviço de Agendas."""

    DEFAULT_TIMEOUT = 10

    @classmethod
    def _get_base_url(cls) -> str:
        """Obtém a URL base do MS-Agendas.

        Returns:
            URL base configurada em ``AGENDAS_API_URL``.

        Raises:
            ValueError: Se ``AGENDAS_API_URL`` não estiver configurada.
        """
        base_url = getattr(settings, "AGENDAS_API_URL", None)
        if not base_url:
            raise ValueError("AGENDAS_API_URL não configurada no settings")
        return base_url.rstrip("/")  # type: ignore[no-any-return]

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
        base_url = cls._get_base_url()
        url = f"{base_url}{path}"
        parametros = {
            "processo_uuid": processo_uuid,
            "cargo": codigo_cargo,
        }
        logger.info(
            "Removendo agendas por processo e cargo no MS-Agendas",
            extra={
                "method": "DELETE",
                "correlation_id": get_correlation_id(),
                "url": url,
                "params": parametros,
                "processo_uuid": processo_uuid,
                "codigo_cargo": codigo_cargo,
            },
        )
        try:
            response = http_client.delete(
                url,
                params=parametros,
                timeout=cls.DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.exception(
                "Erro ao conectar com o microserviço de Agendas: %s", exc
            )
            raise requests.RequestException(
                f"Erro ao conectar com o microserviço de Agendas: {exc}"
            ) from exc

        if response.status_code == status.HTTP_200_OK:
            logger.info(
                "Agendas removidas por processo e cargo no MS-Agendas",
                extra={
                    "method": "DELETE",
                    "correlation_id": get_correlation_id(),
                    "url": url,
                    "params": parametros,
                    "status_code": response.status_code,
                    "response": response.json() if response.content else {},
                },
            )
            return response.json() if response.content else {}

        logger.error(
            "Erro ao remover agendas por processo e cargo: %s - %s",
            response.status_code,
            response.text,
        )
        response.raise_for_status()
        return {}
