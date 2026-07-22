"""Repositório de acesso a dados de ConcursoCandidato."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
    ConcursoCandidatosLote,
)
from candidatos.serializer.concurso_candidato import (
    ConcursoCandidatoCpfUuidSerializer,
    ConcursoCandidatoEliminadoSerializer,
    ConcursoCandidatoReclassificadoSerializer,
    ConcursoCandidatoSerializer,
)
from django.db.models import Count, Prefetch, Q, QuerySet


class ConcursoCandidatoRepository:
    """Consultas e persistência de concurso candidato."""

    @staticmethod
    def serializar(
        concurso_candidato: ConcursoCandidato,
        *,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Converta um concurso candidato em dicionário."""
        kwargs: dict[str, Any] = {}
        if fields is not None:
            kwargs["fields"] = fields
        return ConcursoCandidatoSerializer(concurso_candidato, **kwargs).data

    @classmethod
    def serializar_lista(
        cls,
        itens: list[ConcursoCandidato] | QuerySet[ConcursoCandidato],
        *,
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Converta lista/queryset de concurso candidato em dicionários."""
        kwargs: dict[str, Any] = {}
        if fields is not None:
            kwargs["fields"] = fields
        return ConcursoCandidatoSerializer(itens, many=True, **kwargs).data

    @staticmethod
    def serializar_cpf_uuid(
        itens: list[ConcursoCandidato] | QuerySet[ConcursoCandidato],
    ) -> list[dict[str, Any]]:
        """Serializa apenas uuid e cpf dos itens."""
        return ConcursoCandidatoCpfUuidSerializer(itens, many=True).data

    @staticmethod
    def serializar_reclassificados(
        itens: list[ConcursoCandidato] | QuerySet[ConcursoCandidato],
    ) -> list[dict[str, Any]]:
        """Serializa candidatos reclassificados."""
        return ConcursoCandidatoReclassificadoSerializer(itens, many=True).data

    @staticmethod
    def serializar_eliminados(
        itens: list[ConcursoCandidato] | QuerySet[ConcursoCandidato],
    ) -> list[dict[str, Any]]:
        """Serializa candidatos eliminados."""
        return ConcursoCandidatoEliminadoSerializer(itens, many=True).data

    @classmethod
    def queryset_vazio(cls) -> QuerySet[ConcursoCandidato]:
        """Retorna queryset vazio."""
        return ConcursoCandidato.objects.none()

    @classmethod
    def filtrar_por_lote(
        cls,
        queryset: QuerySet[ConcursoCandidato],
        lote: ConcursoCandidatosLote,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra queryset pelo lote informado."""
        return queryset.filter(lote=lote)

    @classmethod
    def criar(cls, **dados: Any) -> ConcursoCandidato:
        """Cria e persiste um concurso candidato."""
        return ConcursoCandidato.objects.create(**dados)

    @classmethod
    def salvar(
        cls,
        concurso_candidato: ConcursoCandidato,
        *,
        campos_atualizacao: list[str] | None = None,
    ) -> None:
        """Persista alterações em um concurso candidato."""
        if campos_atualizacao:
            concurso_candidato.save(update_fields=campos_atualizacao)
        else:
            concurso_candidato.save()

    @classmethod
    def obter_por_uuid_for_update(
        cls, candidato_uuid: UUID | str
    ) -> ConcursoCandidato:
        """Obtém concurso candidato com lock para update."""
        return ConcursoCandidato.objects.select_for_update().get(
            uuid=candidato_uuid
        )

    @classmethod
    def obter_com_candidato_for_update(
        cls, candidato_uuid: UUID | str
    ) -> ConcursoCandidato:
        """Obtém concurso candidato com candidato e lock para update."""
        return (
            ConcursoCandidato.objects.select_for_update()
            .select_related("candidato")
            .get(uuid=candidato_uuid)
        )

    @classmethod
    def bulk_atualizar_ranking(
        cls, itens: Iterable[ConcursoCandidato]
    ) -> None:
        """Atualiza em lote o campo ranking."""
        ConcursoCandidato.objects.bulk_update(list(itens), ["ranking"])

    @classmethod
    def bulk_atualizar_ranking_escolha(
        cls, itens: Iterable[ConcursoCandidato]
    ) -> None:
        """Atualiza em lote o campo ranking_escolha."""
        ConcursoCandidato.objects.bulk_update(list(itens), ["ranking_escolha"])

    @classmethod
    def bulk_atualizar_campos_lote(
        cls, itens: Iterable[ConcursoCandidato]
    ) -> None:
        """Atualiza em lote campos de lote SIGPEC."""
        ConcursoCandidato.objects.bulk_update(
            list(itens),
            ["numero_lote", "codigo_sigpec", "numero_vaga", "chave_inscrito"],
        )

    @classmethod
    def bulk_atualizar_promocao(
        cls, itens: Iterable[ConcursoCandidato]
    ) -> None:
        """Atualiza em lote campos de promoção para geral."""
        ConcursoCandidato.objects.bulk_update(
            list(itens),
            [
                "categoria_efetiva",
                "promovido_para_geral",
                "promovido_de",
                "promovido_em",
            ],
        )

    @classmethod
    def resetar_campos_lote_por_numero(
        cls, concurso_uuid: UUID | str, numero_lote: Any
    ) -> int:
        """Zera campos de lote dos registros com o mesmo numero_lote."""
        return (
            ConcursoCandidato.objects.filter(
                lote__concurso_uuid=concurso_uuid,
                numero_lote=numero_lote,
            )
            .order_by("-criado_em")
            .update(
                numero_lote=None,
                codigo_sigpec=None,
                numero_vaga=None,
            )
        )

    @classmethod
    def obter_por_inscricao_no_concurso(
        cls, concurso_uuid: UUID | str, codigo_inscricao: str
    ) -> ConcursoCandidato | None:
        """Busca o registro mais recente pela inscrição no concurso."""
        return (
            ConcursoCandidato.objects.select_related("candidato")
            .filter(
                lote__concurso_uuid=concurso_uuid,
                codigo_inscricao=codigo_inscricao,
            )
            .order_by("-criado_em")
            .first()
        )

    @classmethod
    def filtrar_por_uuids_lotes(
        cls, lote_uuids: list[Any]
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra concurso candidatos pelos uuids dos lotes."""
        return ConcursoCandidato.objects.filter(lote__uuid__in=lote_uuids)

    @classmethod
    def agregar_por_categoria(
        cls, queryset: QuerySet[ConcursoCandidato]
    ) -> dict[str, int]:
        """Agrega contagem por categoria_efetiva."""
        contagens = queryset.values("categoria_efetiva").annotate(
            total=Count("uuid")
        )
        por_categoria = {
            item["categoria_efetiva"]: item["total"] for item in contagens
        }
        return {
            "total": sum(por_categoria.values()),
            "geral": por_categoria.get("GERAL", 0),
            "pcd": por_categoria.get("PCD", 0),
            "nna": por_categoria.get("NNA", 0),
        }

    @classmethod
    def filtrar_por_processos(
        cls,
        queryset: QuerySet[ConcursoCandidato],
        processo_uuids: list[UUID | str],
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra queryset pelos processos informados."""
        return queryset.filter(processo_uuid__in=processo_uuids)

    @classmethod
    def filtrar_convocados(
        cls, queryset: QuerySet[ConcursoCandidato]
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra apenas registros convocados."""
        return queryset.filter(foi_convocado=True)

    @classmethod
    def contar(cls, queryset: QuerySet[ConcursoCandidato]) -> int:
        """Conta registros do queryset."""
        return queryset.count()

    @classmethod
    def filtrar_reclassificados_por_categoria(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        codigo_cargo: Any,
        categoria: str,
        filtro_classificacao: dict[str, Any],
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra reclassificados por categoria e limite de classificação."""
        return ConcursoCandidato.objects.filter(
            lote=lote,
            codigo_cargo=codigo_cargo,
            historicos_reclassificacao__desclassificado_de=categoria,
        ).filter(**filtro_classificacao)

    @classmethod
    def filtrar_eliminados_por_filtro_q(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        codigo_cargo: Any,
        filtro_q: Q,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra eliminados do lote/cargo com filtro Q de classificação."""
        return ConcursoCandidato.objects.filter(
            lote=lote, codigo_cargo=codigo_cargo, eliminado=True
        ).filter(filtro_q)

    @classmethod
    def listar_ids(
        cls, queryset: QuerySet[ConcursoCandidato]
    ) -> QuerySet[Any]:
        """Retorna values_list de ids do queryset."""
        return queryset.values_list("id", flat=True)

    @classmethod
    def filtrar_convocados_ativos_por_lote(
        cls,
        *,
        lote: ConcursoCandidatosLote | None,
        codigo_cargo: Any = None,
        uuids: list[Any] | None = None,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra convocados não eliminados do lote."""
        queryset = ConcursoCandidato.objects.filter(
            lote=lote, foi_convocado=True, eliminado=False
        )
        if codigo_cargo:
            queryset = queryset.filter(codigo_cargo=codigo_cargo)
        if uuids:
            queryset = queryset.filter(uuid__in=uuids)
        return queryset

    @classmethod
    def contar_por_categoria_efetiva(
        cls, queryset: QuerySet[ConcursoCandidato], categoria: str
    ) -> int:
        """Conta registros com a categoria efetiva informada."""
        return queryset.filter(categoria_efetiva=categoria).count()

    @classmethod
    def listar_nao_convocados_geral(
        cls,
        *,
        lote: ConcursoCandidatosLote | None,
        codigo_cargo: Any,
        limite: int,
    ) -> QuerySet[ConcursoCandidato]:
        """Retorne gerais não convocados ordenados por classificação."""
        return (
            ConcursoCandidato.objects.filter(
                lote=lote,
                foi_convocado=False,
                eliminado=False,
                codigo_cargo=codigo_cargo,
            )
            .exclude(classificacao__isnull=True)
            .order_by("classificacao")[:limite]
        )

    @classmethod
    def listar_nao_convocados_nna(
        cls,
        *,
        lote: ConcursoCandidatosLote | None,
        codigo_cargo: Any,
        excluir_uuids: Any,
        limite: int,
    ) -> QuerySet[ConcursoCandidato]:
        """Lista candidatos NNA não convocados ordenados por classificação."""
        return (
            ConcursoCandidato.objects.filter(
                lote=lote,
                foi_convocado=False,
                eliminado=False,
                classificacao_nna__isnull=False,
                codigo_cargo=codigo_cargo,
                categoria_efetiva="NNA",
            )
            .exclude(uuid__in=excluir_uuids)
            .order_by("classificacao_nna")[:limite]
        )

    @classmethod
    def listar_nao_convocados_pcd(
        cls,
        *,
        lote: ConcursoCandidatosLote | None,
        codigo_cargo: Any,
        excluir_uuids: Any,
        limite: int,
    ) -> QuerySet[ConcursoCandidato]:
        """Lista candidatos PCD não convocados ordenados por classificação."""
        return (
            ConcursoCandidato.objects.filter(
                lote=lote,
                foi_convocado=False,
                eliminado=False,
                classificacao_pcd__isnull=False,
                codigo_cargo=codigo_cargo,
                categoria_efetiva="PCD",
            )
            .exclude(uuid__in=excluir_uuids)
            .order_by("classificacao_pcd")[:limite]
        )

    @classmethod
    def listar_uuids(
        cls, queryset: QuerySet[ConcursoCandidato]
    ) -> QuerySet[Any]:
        """Retorna values_list de uuids do queryset."""
        return queryset.values_list("uuid", flat=True)

    @classmethod
    def filtrar_reconvocacao(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        candidato_uuids: list[Any],
        codigo_cargo: Any = None,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra candidatos convocados elegíveis à reconvocação."""
        queryset = ConcursoCandidato.objects.filter(
            lote=lote, foi_convocado=True, uuid__in=candidato_uuids
        )
        if codigo_cargo not in (None, ""):
            queryset = queryset.filter(codigo_cargo=codigo_cargo)
        return queryset

    @classmethod
    def filtrar_mandado_judicial(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        codigo_cargo: Any = None,
        nome: Any = None,
        limite: int = 300,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra candidatos com reclassificação por mandado judicial.

        Considera apenas candidatos do lote que possuam ao menos uma
        reclassificação marcada com ``mandado_judicial=True``, ou seja,
        cuja desclassificação foi revertida por determinação judicial.

        Args:
            lote: Lote de candidatos do concurso.
            codigo_cargo: Código do cargo para restringir a busca.
            nome: Trecho do nome do candidato para busca parcial.
            limite: Máximo de registros retornados.

        Returns:
            QuerySet de ConcursoCandidato ordenado por nome do candidato.
        """
        queryset = (
            ConcursoCandidato.objects.select_related("candidato", "lote")
            .prefetch_related(
                Prefetch(
                    "historicos_reclassificacao",
                    queryset=ConcursoCandidatoReclassificacao.objects.filter(
                        mandado_judicial=True
                    ).order_by("-criado_em"),
                    to_attr="reclassificacoes_judiciais",
                )
            )
            .filter(
                lote=lote,
                historicos_reclassificacao__mandado_judicial=True,
            )
            .distinct()
        )
        if codigo_cargo not in (None, ""):
            queryset = queryset.filter(codigo_cargo=codigo_cargo)
        if nome not in (None, ""):
            queryset = queryset.filter(candidato__nome__icontains=nome)
        return queryset.order_by("candidato__nome")[:limite]

    @classmethod
    def filtrar_nao_convocados_por_lote(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        codigo_cargo: Any = None,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra não convocados do lote com relacionamentos."""
        queryset = ConcursoCandidato.objects.select_related(
            "candidato", "lote"
        ).filter(lote=lote, foi_convocado=False)
        if codigo_cargo not in (None, ""):
            queryset = queryset.filter(codigo_cargo=codigo_cargo)
        return queryset

    @classmethod
    def filtrar_por_lote_e_uuids(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        uuids: list[Any],
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra por lote e lista de uuids."""
        return ConcursoCandidato.objects.filter(lote=lote, uuid__in=uuids)

    @classmethod
    def marcar_convocados(
        cls,
        queryset: QuerySet[ConcursoCandidato],
        *,
        processo_uuid: Any,
        data_convocacao: Any,
    ) -> int:
        """Marca registros como convocados."""
        return queryset.update(
            foi_convocado=True,
            processo_uuid=processo_uuid,
            data_convocacao=data_convocacao,
        )

    @classmethod
    def filtrar_convocados_por_processo(
        cls,
        *,
        processo_uuid: Any,
        codigo_cargo: Any = None,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra convocados pelo processo e cargo opcional."""
        queryset = ConcursoCandidato.objects.filter(
            processo_uuid=processo_uuid, foi_convocado=True
        )
        if codigo_cargo:
            queryset = queryset.filter(codigo_cargo=codigo_cargo)
        return queryset

    @classmethod
    def desmarcar_convocados(
        cls, queryset: QuerySet[ConcursoCandidato]
    ) -> int:
        """Remove marcação de convocação dos registros."""
        return queryset.update(
            foi_convocado=False, data_convocacao=None, processo_uuid=None
        )

    @classmethod
    def filtrar_por_uuids(
        cls,
        uuids: list[Any],
        *,
        order_by: str = "classificacao",
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra por uuids com ordenação e relacionamentos."""
        return (
            ConcursoCandidato.objects.filter(uuid__in=uuids)
            .order_by(order_by)
            .select_related("candidato", "lote")
        )

    @classmethod
    def filtrar_por_cpfs_e_processo(
        cls,
        *,
        cpfs: list[str],
        processo_uuid: UUID | str,
        order_by: str = "classificacao",
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra por CPFs e processo com ordenação."""
        return (
            ConcursoCandidato.objects.filter(
                candidato__cpf__in=cpfs, processo_uuid=processo_uuid
            )
            .order_by(order_by)
            .select_related("candidato", "lote")
        )

    @classmethod
    def listar_numeros_lote(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        codigo_cargo: Any = None,
    ) -> QuerySet[Any]:
        """Lista numeros de lote distintos do lote vigente."""
        queryset = ConcursoCandidato.objects.filter(
            lote=lote, numero_lote__isnull=False
        )
        if codigo_cargo:
            queryset = queryset.filter(codigo_cargo=codigo_cargo)
        return (
            queryset.values_list("numero_lote", flat=True)
            .distinct()
            .order_by("numero_lote")
        )

    @classmethod
    def listar_cargos_sigpec(
        cls, *, lote: ConcursoCandidatosLote
    ) -> QuerySet[Any]:
        """Lista cargos distintos com numero_lote preenchido."""
        return (
            ConcursoCandidato.objects.filter(
                lote=lote, numero_lote__isnull=False
            )
            .values("codigo_cargo", "descricao_cargo")
            .distinct()
            .order_by("codigo_cargo")
        )

    @classmethod
    def buscar_por_filtro_candidato(
        cls, filtro: Q, *, limite: int = 300
    ) -> QuerySet[ConcursoCandidato]:
        """Busca concurso candidatos por filtro Q do candidato."""
        return (
            ConcursoCandidato.objects.filter(filtro)
            .select_related("candidato", "lote")
            .order_by("candidato__nome")[:limite]
        )

    @classmethod
    def filtrar_reclassificados_por_processo(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        processo_uuid: UUID | str,
        desclassificado_de: str,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra reclassificados para GERAL no processo informado."""
        return (
            ConcursoCandidato.objects.select_related("candidato", "lote")
            .filter(lote=lote, eliminado=False, categoria_efetiva="GERAL")
            .filter(historicos_reclassificacao__processo_uuid=processo_uuid)
            .filter(
                historicos_reclassificacao__desclassificado_de=desclassificado_de
            )
            .distinct()
        )

    @classmethod
    def filtrar_eliminados_por_processo_e_classificacao(
        cls,
        *,
        lote: ConcursoCandidatosLote,
        processo_uuid: UUID | str,
        classificacao_min: Any,
        classificacao_max: Any,
    ) -> QuerySet[ConcursoCandidato]:
        """Filtra eliminados do processo no intervalo de classificação."""
        return (
            ConcursoCandidato.objects.select_related("candidato", "lote")
            .filter(lote=lote, eliminado=True)
            .filter(
                classificacao__lte=classificacao_max,
                classificacao__gte=classificacao_min,
            )
            .filter(historicos_eliminacao__processo_uuid=processo_uuid)
            .distinct()
        )
