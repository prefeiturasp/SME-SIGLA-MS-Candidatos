"""Módulo service/calculo_habilitados_service."""

from __future__ import annotations

import contextlib
import math
from typing import Any

from django.db.models import Q
from django.utils import timezone

from candidatos.models import ConcursoCandidato, Parametrizacao

from .ranking_service import atualizar_ranking, atualizar_ranking_escolha


def calcular_quantidade_nna(
    total_candidatos: Any, porcentagem_nna: Any
) -> Any:
    """Calcula a quantidade de vagas reservadas a NNA.

    Args:
        total_candidatos: Total de candidatos considerados no cálculo.
        porcentagem_nna: Percentual aplicado sobre o total para NNA.

    Returns:
        Quantidade de vagas NNA, arredondada para cima a partir da
        porcentagem sobre o total.
    """
    return math.ceil(total_candidatos * porcentagem_nna)


def calcular_quantidade_pcd(
    total_candidatos: Any, porcentagem_pcd: Any
) -> Any:
    """Calcula a quantidade de vagas reservadas a PCD.

    Args:
        total_candidatos: Total de candidatos considerados no cálculo.
        porcentagem_pcd: Percentual aplicado sobre o total para PCD.

    Returns:
        Quantidade de vagas PCD, obtida pela porcentagem sobre o total com
        arredondamento matemático.
    """
    valor = total_candidatos * porcentagem_pcd
    frac = valor - math.floor(valor)
    return math.ceil(valor) if frac >= 0.5 else math.floor(valor)


def calcular_quantidade_geral(
    total_candidatos: Any, porcentagem_nna: Any, porcentagem_pcd: Any
) -> Any:
    """Calcula a quantidade de vagas da ampla concorrência.

    Args:
        total_candidatos: Total de candidatos considerados no cálculo.
        porcentagem_nna: Percentual reservado a NNA.
        porcentagem_pcd: Percentual reservado a PCD.

    Returns:
        Quantidade de vagas gerais, equivalente ao total menos as reservas
        de NNA e PCD.
    """
    return (
        total_candidatos
        - calcular_quantidade_nna(total_candidatos, porcentagem_nna)
        - calcular_quantidade_pcd(total_candidatos, porcentagem_pcd)
    )


def calcular_posicao_nna(posicao: Any) -> Any:
    """Calcula a posição absoluta na sequência para a n-ésima vaga NNA.

    Args:
        posicao: Índice da vaga NNA (1-based).

    Returns:
        Posição absoluta na fila de convocação conforme a regra 5n - 4.
    """
    return 5 * posicao - 4


def calcular_posicao_pcd(posicao: Any) -> Any:
    """Calcula a posição absoluta na sequência para a n-ésima vaga PCD.

    Args:
        posicao: Índice da vaga PCD (1-based).

    Returns:
        Posição absoluta na fila de convocação (regra 10 + (n - 1) * 20).
    """
    return 10 + (posicao - 1) * 20


def _safe_max_classificacao(final_itens: Any, classificacao_attr: str) -> Any:
    """Retorna o maior valor inteiro encontrado no atributo de classificação.

    Args:
        final_itens: Candidatos já selecionados para a convocação.
        classificacao_attr: Atributo consultado (``classificacao``,
            ``classificacao_nna`` ou ``classificacao_pcd``).

    Returns:
        Maior classificação encontrada ou ``None`` se inválido.
    """
    try:
        valores = []
        for item in final_itens:
            try:
                if classificacao_attr == "classificacao":
                    if getattr(item, "classificacao_nna", None) is not None:
                        continue
                    if getattr(item, "classificacao_pcd", None) is not None:
                        continue
                valor = getattr(item, classificacao_attr, None)
                if valor is None:
                    continue
                valor_int = int(valor)
                if valor_int:
                    valores.append(valor_int)
            except Exception:
                continue
        return max(valores) if valores else None
    except Exception:
        return None


def _atualizar_processo_uuid_para_reclassificados(
    final_itens: Any,
    categoria: str,
    classificacao_attr: str,
    processo_uuid: Any,
    lote: Any,
    codigo_cargo: Any,
) -> None:
    """Atualiza processo_uuid nos históricos de reclassificação.

    Args:
        final_itens: Candidatos convocados nesta sequência.
        categoria: Categoria desclassificada (``NNA`` ou ``PCD``).
        classificacao_attr: Atributo de classificação usado como referência.
        processo_uuid: UUID do processo de convocação atual.
        lote: Lote do concurso.
        codigo_cargo: Código do cargo filtrado.

    Returns:
        Nenhum valor; atualiza registros de reclassificação no banco.
    """
    try:
        if not processo_uuid:
            return
        limite = _safe_max_classificacao(final_itens, classificacao_attr)
        if not limite:
            return
        from candidatos.models import ConcursoCandidatoReclassificacao

        filtro_classificacao = {f"{classificacao_attr}__lt": limite}
        reclassificados_qs = ConcursoCandidato.objects.filter(
            lote=lote,
            codigo_cargo=codigo_cargo,
            historicos_reclassificacao__desclassificado_de=categoria,
        ).filter(**filtro_classificacao)
        if reclassificados_qs.exists():
            ConcursoCandidatoReclassificacao.objects.filter(
                concurso_candidato__in=reclassificados_qs.values_list(
                    "id", flat=True
                ),
                processo_uuid=None,
                desclassificado_de=categoria,
            ).update(processo_uuid=processo_uuid)
    except Exception:
        return


def _atualizar_processo_uuid_para_eliminados(
    final_itens: Any, processo_uuid: Any, lote: Any, codigo_cargo: Any
) -> None:
    """Atualiza processo_uuid nos históricos de eliminação abaixo dos limites.

    Args:
        final_itens: Candidatos convocados nesta sequência.
        processo_uuid: UUID do processo de convocação atual.
        lote: Lote do concurso.
        codigo_cargo: Código do cargo filtrado.

    Returns:
        Nenhum valor; atualiza registros de eliminação no banco.
    """
    try:
        if not processo_uuid:
            return
        limites = {
            "classificacao": _safe_max_classificacao(
                final_itens, "classificacao"
            ),
            "classificacao_nna": _safe_max_classificacao(
                final_itens, "classificacao_nna"
            ),
            "classificacao_pcd": _safe_max_classificacao(
                final_itens, "classificacao_pcd"
            ),
        }
        filtro_q = Q()
        for attr, limite in limites.items():
            if limite:
                filtro_q |= Q(**{f"{attr}__lt": limite})
        if not filtro_q:
            return
        from candidatos.models import ConcursoCandidatoEliminacao

        eliminados_qs = ConcursoCandidato.objects.filter(
            lote=lote, codigo_cargo=codigo_cargo, eliminado=True
        ).filter(filtro_q)
        if eliminados_qs.exists():
            ConcursoCandidatoEliminacao.objects.filter(
                concurso_candidato__in=eliminados_qs.values_list(
                    "id", flat=True
                ),
                processo_uuid=None,
            ).update(processo_uuid=processo_uuid)
    except Exception:
        return


def gerar_sequencia_convocados(
    total_convocados: Any,
    lote: Any = None,
    escolhas_candidato_uuids: Any = None,
    codigo_cargo: Any = None,
    processo_uuid: Any = None,
) -> Any:
    """Gera a sequência de convocação com rótulos G, NNA e PCD.

    Args:
        total_convocados: Quantidade de candidatos a convocar nesta rodada.
        lote: Lote do concurso (opcional).
        escolhas_candidato_uuids: UUIDs de candidatos com escolha confirmada.
        codigo_cargo: Filtro por cargo (opcional).
        processo_uuid: UUID do processo para vincular históricos.

    Returns:
        Tupla com a lista de candidatos convocados e as porcentagens NNA e PCD.
    """
    parametrizacao = Parametrizacao.objects.first()
    porcentagem_nna = parametrizacao.porcentagem_nna  # type: ignore[union-attr]
    porcentagem_pcd = parametrizacao.porcentagem_pcd  # type: ignore[union-attr]
    if total_convocados <= 0:
        return []
    convocados_qs = ConcursoCandidato.objects.filter(
        lote=lote, foi_convocado=True, eliminado=False
    )
    if codigo_cargo:
        convocados_qs = convocados_qs.filter(codigo_cargo=codigo_cargo)
    num_escolhas = (
        len(escolhas_candidato_uuids)
        if escolhas_candidato_uuids is not None
        else 0
    )
    if num_escolhas > 0:
        convocados_qs = convocados_qs.filter(uuid__in=escolhas_candidato_uuids)
    convocados_total = convocados_qs.count()
    convocados_nna = convocados_qs.filter(categoria_efetiva="NNA").count()
    convocados_pcd = convocados_qs.filter(categoria_efetiva="PCD").count()
    convocados_geral = convocados_qs.filter(categoria_efetiva="GERAL").count()
    cumul_total = convocados_total + total_convocados
    cumul_nna = calcular_quantidade_nna(cumul_total, porcentagem_nna)
    cumul_pcd = calcular_quantidade_pcd(cumul_total, porcentagem_pcd)
    cumul_geral = calcular_quantidade_geral(
        cumul_total, porcentagem_nna, porcentagem_pcd
    )
    nna_total = max(0, cumul_nna - convocados_nna)
    pcd_total = max(0, cumul_pcd - convocados_pcd)
    geral_total = max(0, cumul_geral - convocados_geral)
    sequencia = ["G"] * total_convocados

    def calcular_quantidades_por_tipo(geral: Any, nna: Any, pcd: Any) -> Any:
        """Seleciona candidatos por categoria (geral, NNA e PCD).

        Args:
            geral: Quantidade de vagas de ampla concorrência.
            nna: Quantidade de vagas NNA.
            pcd: Quantidade de vagas PCD.

        Returns:
            Tupla com os querysets por categoria e indicadores de faltantes.
        """
        qs_geral = (
            ConcursoCandidato.objects.filter(
                lote=lote,
                foi_convocado=False,
                eliminado=False,
                codigo_cargo=codigo_cargo,
            )
            .exclude(classificacao__isnull=True)
            .order_by("classificacao")[:geral]
        )
        uuids_qs_geral = qs_geral.values_list("uuid", flat=True)
        qs_nna = (
            ConcursoCandidato.objects.filter(
                lote=lote,
                foi_convocado=False,
                eliminado=False,
                classificacao_nna__isnull=False,
                codigo_cargo=codigo_cargo,
                categoria_efetiva="NNA",
            )
            .exclude(uuid__in=uuids_qs_geral)
            .order_by("classificacao_nna")[:nna]
        )
        tem_nna_faltante, quantidade_faltante_nna = (
            qs_nna.count() < nna,
            nna - qs_nna.count(),
        )
        qs_pcd = (
            ConcursoCandidato.objects.filter(
                lote=lote,
                foi_convocado=False,
                eliminado=False,
                classificacao_pcd__isnull=False,
                codigo_cargo=codigo_cargo,
                categoria_efetiva="PCD",
            )
            .exclude(uuid__in=uuids_qs_geral)
            .order_by("classificacao_pcd")[:pcd]
        )
        tem_pcd_faltante, quantidade_faltante_pcd = (
            qs_pcd.count() < pcd,
            pcd - qs_pcd.count(),
        )
        return (
            qs_geral,
            qs_nna,
            qs_pcd,
            tem_nna_faltante,
            quantidade_faltante_nna,
            tem_pcd_faltante,
            quantidade_faltante_pcd,
        )

    def calcular_com_recalculo_se_necessario(
        geral: Any, nna: Any, pcd: Any
    ) -> Any:
        """Recalcula quantidades por tipo quando faltam candidatos NNA ou PCD.

        Args:
            geral: Quantidade de vagas de ampla concorrência.
            nna: Quantidade de vagas NNA.
            pcd: Quantidade de vagas PCD.

        Returns:
            Tupla com os querysets por categoria após eventual recálculo.
        """
        (
            qs_geral,
            qs_nna,
            qs_pcd,
            tem_nna_faltante,
            quantidade_faltante_nna,
            tem_pcd_faltante,
            quantidade_faltante_pcd,
        ) = calcular_quantidades_por_tipo(geral, nna, pcd)
        if tem_nna_faltante or tem_pcd_faltante:
            geral = geral + quantidade_faltante_nna + quantidade_faltante_pcd
            nna = nna + quantidade_faltante_nna
            pcd = pcd + quantidade_faltante_pcd
            return calcular_quantidades_por_tipo(geral, nna, pcd)
        return (qs_geral, qs_nna, qs_pcd)

    qs_geral, qs_nna, qs_pcd, *args = calcular_com_recalculo_se_necessario(
        geral_total, nna_total, pcd_total
    )
    nna_list = list(qs_nna)
    pcd_list = list(qs_pcd)
    geral_list = list(qs_geral)
    for obj in geral_list:
        try:
            obj.categoria_efetiva = "GERAL"
            obj.promovido_para_geral = False
            obj.promovido_de = None
            obj.promovido_em = None
        except Exception:
            pass
        obj.save()
    for obj in nna_list:
        try:
            obj.categoria_efetiva = "NNA"
            obj.promovido_para_geral = False
            obj.promovido_de = None
            obj.promovido_em = None
        except Exception:
            pass
        obj.save()
    for obj in pcd_list:
        try:
            obj.categoria_efetiva = "PCD"
            obj.promovido_para_geral = False
            obj.promovido_de = None
            obj.promovido_em = None
        except Exception:
            pass
        obj.save()
    idx_nna = idx_pcd = idx_geral = 0
    promovidos_to_update = []
    now = timezone.now()
    for obj in geral_list:
        try:
            if getattr(obj, "classificacao_nna", None) is not None and (
                not obj.historicos_reclassificacao.filter(
                    desclassificado_de="NNA"
                ).exists()
            ):
                obj.categoria_efetiva = "GERAL"
                obj.promovido_para_geral = True
                obj.promovido_de = "NNA"
                obj.promovido_em = now
                promovidos_to_update.append(obj)
            elif getattr(obj, "classificacao_pcd", None) is not None and (
                not obj.historicos_reclassificacao.filter(
                    desclassificado_de="PCD"
                ).exists()
            ):
                obj.categoria_efetiva = "GERAL"
                obj.promovido_para_geral = True
                obj.promovido_de = "PCD"
                obj.promovido_em = now
                promovidos_to_update.append(obj)
        except Exception:
            continue
    if promovidos_to_update:
        ConcursoCandidato.objects.bulk_update(
            promovidos_to_update,
            [
                "categoria_efetiva",
                "promovido_para_geral",
                "promovido_de",
                "promovido_em",
            ],
        )
    offset = convocados_total
    pcd_positions = []
    for i in range(1, cumul_pcd + 1):
        pos_abs = calcular_posicao_pcd(i)
        if offset < pos_abs <= cumul_total:
            pcd_positions.append(pos_abs - offset - 1)
            if len(pcd_positions) >= pcd_total:
                break
    nna_positions = []
    for i in range(1, cumul_nna + 1):
        pos_abs = 3 if i == 1 and cumul_total >= 3 else calcular_posicao_nna(i)
        if offset < pos_abs <= cumul_total:
            nna_positions.append(pos_abs - offset - 1)
            if len(nna_positions) >= nna_total:
                break

    def place_at_or_next_free(
        index_list: Any, label: Any, remaining: Any
    ) -> Any:
        """Posiciona rótulos na sequência ou na próxima posição livre.

        Args:
            index_list: Posições preferenciais na sequência.
            label: Rótulo a inserir (``NNA`` ou ``PCD``).
            remaining: Quantidade restante a posicionar.

        Returns:
            Quantidade de rótulos efetivamente posicionados.
        """
        placed = 0
        for idx in index_list:
            if placed >= remaining:
                break
            j = idx
            while j < total_convocados and sequencia[j] != "G":
                j += 1
            if j < total_convocados:
                sequencia[j] = label
                placed += 1
        return placed

    pcd_placed = place_at_or_next_free(pcd_positions, "PCD", pcd_total)
    nna_placed = place_at_or_next_free(nna_positions, "NNA", nna_total)

    def backfill_remaining(label: Any, remaining_to_place: Any) -> Any:
        """Preenche posições G restantes com o rótulo informado.

        Args:
            label: Rótulo a inserir (``NNA`` ou ``PCD``).
            remaining_to_place: Quantidade ainda não posicionada.

        Returns:
            Quantidade de posições preenchidas.
        """
        placed = 0
        for i in range(total_convocados):
            if placed >= remaining_to_place:
                break
            if sequencia[i] == "G":
                sequencia[i] = label
                placed += 1
        return placed

    if pcd_placed < pcd_total:
        backfill_remaining("PCD", pcd_total - pcd_placed)
    if nna_placed < nna_total:
        backfill_remaining("NNA", nna_total - nna_placed)
    resultado_itens = [None] * total_convocados

    def pop_from(label: Any) -> Any:
        """Remove e retorna o próximo candidato da fila da categoria.

        Args:
            label: Categoria da fila (``G``, ``NNA`` ou ``PCD``).

        Returns:
            Próximo ``ConcursoCandidato`` da fila ou ``None`` se esgotada.
        """
        nonlocal idx_nna, idx_pcd, idx_geral
        if label == "NNA" and idx_nna < len(nna_list):
            item = nna_list[idx_nna]
            idx_nna += 1
            return item
        if label == "PCD" and idx_pcd < len(pcd_list):
            item = pcd_list[idx_pcd]
            idx_pcd += 1
            return item
        if label == "G" and idx_geral < len(geral_list):
            item = geral_list[idx_geral]
            idx_geral += 1
            return item
        return None

    for i, label in enumerate(sequencia):
        item = pop_from(label)
        if item is None:
            if label != "NNA":
                item = pop_from("NNA")
            if item is None and label != "PCD":
                item = pop_from("PCD")
            if item is None and label != "G":
                item = pop_from("G")
        if item is not None:
            with contextlib.suppress(Exception):
                item.ranking = i + 1
            resultado_itens[i] = item
    final_itens = [it for it in resultado_itens if it is not None]
    with contextlib.suppress(Exception):
        [str(it.uuid) for it in final_itens]  # type: ignore[attr-defined]
    _atualizar_processo_uuid_para_reclassificados(
        final_itens=final_itens,
        categoria="PCD",
        classificacao_attr="classificacao_pcd",
        processo_uuid=processo_uuid,
        lote=lote,
        codigo_cargo=codigo_cargo,
    )
    _atualizar_processo_uuid_para_reclassificados(
        final_itens=final_itens,
        categoria="NNA",
        classificacao_attr="classificacao_nna",
        processo_uuid=processo_uuid,
        lote=lote,
        codigo_cargo=codigo_cargo,
    )
    _atualizar_processo_uuid_para_eliminados(
        final_itens=final_itens,
        processo_uuid=processo_uuid,
        lote=lote,
        codigo_cargo=codigo_cargo,
    )
    atualizar_ranking(final_itens)
    atualizar_ranking_escolha(final_itens)
    return (final_itens, porcentagem_nna, porcentagem_pcd)
