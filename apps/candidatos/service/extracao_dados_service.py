"""Agregações para a extração de dados de habilitados / convocados.

Toda contagem parte dos registros de ``ConcursoCandidato`` filtrados por
``concurso_uuid``. Quando nenhum concurso é informado, considera todos os
registros existentes.
"""

from typing import Any
from uuid import UUID

from candidatos.models import ConcursoCandidato
from candidatos.repository import ConcursoCandidatoRepository
from django.db.models.query import QuerySet

CATEGORIAS = ("GERAL", "PCD", "NNA")


class ExtracaoDadosService:
    """Service para agregações de habilitados e convocados."""

    @classmethod
    def montar_extracao_dados(
        cls,
        concurso_uuid: UUID | str | None = None,
        filtros: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Monta o dicionário de indicadores de habilitados e convocações.

        Args:
            concurso_uuid: Concurso a restringir; ausente → todos os concursos.
            filtros: Lista de ``{ano, processo_uuids}``; ausente (ou vazia) →
                agregado direto na raiz, sem quebra por ano.

        Returns:
            Dicionário com ``habilitados`` e, por ano (ou na raiz), os
            ``convocados`` e ``nao-convocados`` do escopo.
        """
        habilitados = cls._contar_habilitados(concurso_uuid)
        resultado: dict[str, Any] = {"habilitados": habilitados}

        if filtros:
            for filtro in filtros:
                ano = str(filtro["ano"])
                processo_uuids = filtro["processo_uuids"]
                habilitados_ano = cls._contar_habilitados_por_processos(
                    concurso_uuid, processo_uuids
                )
                convocados = cls._contar_convocados(
                    concurso_uuid, processo_uuids
                )
                resultado[ano] = {
                    "habilitados": habilitados_ano,
                    "convocados": convocados,
                    "nao-convocados": habilitados["total"] - convocados,
                }
        else:
            convocados = cls._contar_convocados(concurso_uuid)
            resultado.update(
                {
                    "convocados": convocados,
                    "nao-convocados": habilitados["total"] - convocados,
                }
            )

        return resultado

    @staticmethod
    def _queryset_base(
        concurso_uuid: UUID | str | None = None,
    ) -> QuerySet[ConcursoCandidato]:
        """Queryset canônico de habilitados filtrado por concurso.

        Args:
            concurso_uuid: Concurso a restringir; ausente → todos os concursos.

        Returns:
            ``ConcursoCandidato`` filtrado pelo escopo informado.
        """
        if concurso_uuid:
            return ConcursoCandidatoRepository.filtrar_por_concurso_uuid(
                ConcursoCandidato.objects.all(), concurso_uuid
            )
        return ConcursoCandidato.objects.all()

    @staticmethod
    def _agregar_por_categoria(
        qs: QuerySet[ConcursoCandidato],
    ) -> dict[str, int]:
        """Agrega a contagem por ``categoria_efetiva``.

        Args:
            qs: Queryset de ``ConcursoCandidato`` a agregar.

        Returns:
            Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
            ``nna``.
        """
        return ConcursoCandidatoRepository.agregar_por_categoria(qs)

    @classmethod
    def _contar_habilitados(
        cls,
        concurso_uuid: UUID | str | None = None,
    ) -> dict[str, int]:
        """Conta habilitados por categoria efetiva no escopo informado.

        Args:
            concurso_uuid: Concurso a restringir; ausente → todos os concursos.

        Returns:
            Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
            ``nna``.
        """
        return cls._agregar_por_categoria(cls._queryset_base(concurso_uuid))

    @classmethod
    def _contar_habilitados_por_processos(
        cls,
        concurso_uuid: UUID | str | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> dict[str, int]:
        """Conta habilitados por categoria no escopo dos processos informados.

        Args:
            concurso_uuid: Concurso a restringir; ausente → todos os concursos.
            processo_uuids: Processos a filtrar; vazio → zeros.

        Returns:
            Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
            ``nna`` no escopo, restrito aos processos informados.
        """
        if not processo_uuids:
            return {"total": 0, "geral": 0, "pcd": 0, "nna": 0}

        qs = ConcursoCandidatoRepository.filtrar_por_processos(
            cls._queryset_base(concurso_uuid), processo_uuids
        )
        return cls._agregar_por_categoria(qs)

    @classmethod
    def _contar_convocados(
        cls,
        concurso_uuid: UUID | str | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> int:
        """Conta ``foi_convocado=True`` no escopo informado.

        Args:
            concurso_uuid: Concurso a restringir; ausente → todos os concursos.
            processo_uuids: Processos a filtrar. ``None`` → modo "ALL"
                (todos os convocados do escopo); lista → filtra também
                pelos processos do ano.

        Returns:
            Quantidade de convocados no escopo informado.
        """
        qs = ConcursoCandidatoRepository.filtrar_convocados(
            cls._queryset_base(concurso_uuid)
        )
        if processo_uuids is not None:
            qs = ConcursoCandidatoRepository.filtrar_por_processos(
                qs, processo_uuids
            )
        return ConcursoCandidatoRepository.contar(qs)
