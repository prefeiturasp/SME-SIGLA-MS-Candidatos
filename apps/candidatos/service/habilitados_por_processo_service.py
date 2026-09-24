"""Agregação de habilitados por processo e categoria efetiva."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from candidatos.repository import ConcursoCandidatoRepository

CATEGORIAS = ("GERAL", "NNA", "PCD")


class HabilitadosPorProcessoService:
    """Service para agregar convocados por processo e categoria."""

    @staticmethod
    def _bloco_vazio() -> dict[str, dict[str, Any]]:
        return {
            cat: {"total": 0, "candidatos_uuids": []} for cat in CATEGORIAS
        }

    @classmethod
    def montar_por_processos_e_tipo_vaga(
        cls,
        processo_uuids: list[UUID | str],
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """Monta totais e UUIDs de candidatos por processo/categoria.

        Args:
            processo_uuids: Lista de UUIDs de processos de convocação.

        Returns:
            Estrutura::

                {
                    "<processo_uuid>": {
                        "GERAL": {"total": N, "candidatos_uuids": [...]},
                        "NNA": {"total": N, "candidatos_uuids": [...]},
                        "PCD": {"total": N, "candidatos_uuids": [...]},
                    }
                }
        """
        resultado: dict[str, dict[str, dict[str, Any]]] = {
            str(pid): cls._bloco_vazio() for pid in processo_uuids
        }
        if not processo_uuids:
            return resultado

        rows = ConcursoCandidatoRepository.listar_convocados_por_processos(
            processo_uuids
        )
        for row in rows:
            processo_key = str(row["processo_uuid"])
            categoria = row.get("categoria_efetiva") or "GERAL"
            if categoria not in CATEGORIAS:
                categoria = "GERAL"
            if processo_key not in resultado:
                resultado[processo_key] = cls._bloco_vazio()
            candidato_uuid = row.get("uuid")
            if candidato_uuid is None:
                continue
            resultado[processo_key][categoria]["candidatos_uuids"].append(
                str(candidato_uuid)
            )
            resultado[processo_key][categoria]["total"] += 1
        return resultado
