"""Repositório de acesso a dados de Candidato."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from candidatos.models import Candidato
from candidatos.serializer.candidato import CandidatoSerializer
from django.db.models import QuerySet


class CandidatoRepository:
    """Consultas e persistência de candidatos."""

    @staticmethod
    def serializar(candidato: Candidato) -> dict[str, Any]:
        """Converta um candidato em dicionário."""
        return CandidatoSerializer(candidato).data

    @classmethod
    def serializar_lista(
        cls, candidatos: list[Candidato] | QuerySet[Candidato]
    ) -> list[dict[str, Any]]:
        """Converta uma lista ou queryset de candidatos em dicionários."""
        return CandidatoSerializer(candidatos, many=True).data

    @classmethod
    def buscar_todos(cls) -> QuerySet[Candidato]:
        """Retorna o queryset base de todos os candidatos."""
        return Candidato.objects.all()

    @classmethod
    def criar(cls, **dados: Any) -> Candidato:
        """Cria e persiste um candidato."""
        return Candidato.objects.create(**dados)

    @classmethod
    def bulk_atualizar_registro_vinculo(
        cls, candidatos: Iterable[Candidato]
    ) -> None:
        """Atualiza em lote registro_funcional e vinculo."""
        Candidato.objects.bulk_update(
            list(candidatos), ["registro_funcional", "vinculo"]
        )

    @classmethod
    def obter_por_cpf(cls, cpf: str) -> Candidato | None:
        """Retorna o candidato mais recente com o CPF informado."""
        if not cpf:
            return None
        return Candidato.objects.filter(cpf=cpf).order_by("-id").first()

    @classmethod
    def salvar(
        cls,
        candidato: Candidato,
        *,
        campos_atualizacao: list[str] | None = None,
    ) -> None:
        """Persista alterações em um candidato."""
        if campos_atualizacao:
            candidato.save(update_fields=campos_atualizacao)
        else:
            candidato.save()

    @classmethod
    def existe_por_cpf(cls, cpf: str) -> bool:
        """Verifica se já existe candidato com o CPF informado."""
        return Candidato.objects.filter(cpf=cpf).exists()

    @classmethod
    def existe_por_email(cls, email: str) -> bool:
        """Verifica se já existe candidato com o e-mail informado."""
        return Candidato.objects.filter(email=email).exists()

    @classmethod
    def contar(cls) -> int:
        """Retorna a quantidade total de candidatos."""
        return Candidato.objects.count()

    @classmethod
    def contar_por_status(cls, status: str) -> int:
        """Retorna a quantidade de candidatos com o status informado."""
        return Candidato.objects.filter(status=status).count()

    @classmethod
    def excluir_todos(cls) -> None:
        """Remove todos os candidatos."""
        Candidato.objects.all().delete()
