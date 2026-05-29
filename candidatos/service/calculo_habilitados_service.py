import contextlib
import math

from django.db.models import Q
from django.utils import timezone

from candidatos.models import ConcursoCandidato, Parametrizacao

from .ranking_service import atualizar_ranking, atualizar_ranking_escolha


def calcular_quantidade_nna(total_candidatos, porcentagem_nna):
    return math.ceil(total_candidatos * porcentagem_nna)


def calcular_quantidade_pcd(total_candidatos, porcentagem_pcd):
    valor = total_candidatos * porcentagem_pcd
    frac = valor - math.floor(valor)
    return math.ceil(valor) if frac >= 0.5 else math.floor(valor)


def calcular_quantidade_geral(
    total_candidatos, porcentagem_nna, porcentagem_pcd
):
    return (
        total_candidatos
        - calcular_quantidade_nna(total_candidatos, porcentagem_nna)
        - calcular_quantidade_pcd(total_candidatos, porcentagem_pcd)
    )


def calcular_posicao_nna(posicao):
    return (5 * posicao) - 4


def calcular_posicao_pcd(posicao):
    return 10 + (posicao - 1) * 20


def _safe_max_classificacao(final_itens, classificacao_attr: str):
    """
    Retorna o maior valor inteiro encontrado no atributo de classificação
    informado dentre os itens finais. Ignora valores nulos/inválidos.
    """
    try:
        valores = []
        for item in final_itens:
            try:
                # Quando for 'classificacao' (GERAL), considerar apenas itens que tenham  # noqa: E501
                # 'classificacao' preenchido e NÃO tenham classificacao_nna/pcd (i.e., são gerais)  # noqa: E501
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
    final_itens,
    categoria: str,
    classificacao_attr: str,
    processo_uuid,
    lote,
    codigo_cargo,
):
    """
    Atualiza processo_uuid nos históricos de reclassificação para candidatos
    que foram
    reclassificados da categoria indicada (NNA/PCD) e cuja classificação
    original é menor
    que o maior valor de classificação efetivamente utilizado em final_itens.
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
        # Não deve quebrar o fluxo principal de geração
        return


def _atualizar_processo_uuid_para_eliminados(
    final_itens,
    processo_uuid,
    lote,
    codigo_cargo,
):
    """
    Atualiza processo_uuid nos históricos de eliminação para candidatos que
    foram eliminados
    e cuja classificação (geral/nna/pcd) é menor do que o maior valor de
    classificação
    efetivamente utilizado em final_itens, considerando todos os tipos de
    classificação.
    """
    try:
        if not processo_uuid:
            return
        # Limites máximos por tipo de classificação observados no lote final
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
        # Monta filtro combinado por qualquer classificação menor que o limite correspondente  # noqa: E501
        filtro_q = Q()
        for attr, limite in limites.items():
            if limite:
                filtro_q |= Q(**{f"{attr}__lt": limite})
        if not filtro_q:
            return
        from candidatos.models import ConcursoCandidatoEliminacao

        eliminados_qs = ConcursoCandidato.objects.filter(
            lote=lote,
            codigo_cargo=codigo_cargo,
            eliminado=True,
        ).filter(filtro_q)
        if eliminados_qs.exists():
            ConcursoCandidatoEliminacao.objects.filter(
                concurso_candidato__in=eliminados_qs.values_list(
                    "id", flat=True
                ),
                processo_uuid=None,
            ).update(processo_uuid=processo_uuid)
    except Exception:
        # Não deve quebrar o fluxo principal de geração
        return


def gerar_sequencia_convocados(
    total_convocados,
    lote=None,
    escolhas_candidato_uuids=None,
    codigo_cargo=None,
    processo_uuid=None,
):
    """
    Gera a sequência de convocação com rótulos 'G', 'NNA' e 'PCD', respeitando:
    - Totais por tipo (NNA: ceil(20%), PCD: arredonda pra cima apenas se frac
    >= 0.5; Geral = resto)
    - Posições-alvo de NNA/PCD: 10, 30, 50, ... (calcular_posicao_*).
      Em caso de colisão, PCD tem prioridade (é alocado primeiro) e o outro
      tipo é deslocado
      para o próximo índice disponível.
    """
    parametrizacao = Parametrizacao.objects.first()
    porcentagem_nna = parametrizacao.porcentagem_nna
    porcentagem_pcd = parametrizacao.porcentagem_pcd
    if total_convocados <= 0:
        return []
    # Quantidade já convocada (acumulado) por categoria efetiva
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

    # Totais cumulativos alvo (já convocados + novo lote)
    cumul_total = convocados_total + total_convocados
    cumul_nna = calcular_quantidade_nna(cumul_total, porcentagem_nna)
    cumul_pcd = calcular_quantidade_pcd(cumul_total, porcentagem_pcd)
    cumul_geral = calcular_quantidade_geral(
        cumul_total, porcentagem_nna, porcentagem_pcd
    )

    # Necessidade deste lote (cumulativo alvo - já convocados)
    nna_total = max(0, cumul_nna - convocados_nna)
    pcd_total = max(0, cumul_pcd - convocados_pcd)
    geral_total = max(0, cumul_geral - convocados_geral)
    sequencia = ["G"] * total_convocados

    def calcular_quantidades_por_tipo(geral, nna, pcd):
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

    def calcular_com_recalculo_se_necessario(geral, nna, pcd):
        """
        Executa o cálculo por tipo e, caso faltem NNA/PCD, recalcula apenas
        mais uma vez
        ajustando os totais (no máximo 2 execuções).
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

    (qs_geral, qs_nna, qs_pcd, *args) = calcular_com_recalculo_se_necessario(
        geral_total, nna_total, pcd_total
    )
    nna_list = list(qs_nna)
    pcd_list = list(qs_pcd)
    geral_list = list(qs_geral)
    # Inicializa categoria efetiva (somente em memória, sem persistir)
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

    # As listas já são retornadas do banco na quantidade e ordem corretas.
    # Marcar como promovidos, persistindo no banco, os itens que entraram na geral_list mas possuem cota NNA/PCD  # noqa: E501
    promovidos_to_update = []
    now = timezone.now()
    for obj in geral_list:
        try:
            if (
                getattr(obj, "classificacao_nna", None) is not None
                and not obj.historicos_reclassificacao.filter(
                    desclassificado_de="NNA"
                ).exists()
            ):
                # promovido de NNA para GERAL
                obj.categoria_efetiva = "GERAL"
                obj.promovido_para_geral = True
                obj.promovido_de = "NNA"
                obj.promovido_em = now
                promovidos_to_update.append(obj)
            elif (
                getattr(obj, "classificacao_pcd", None) is not None
                and not obj.historicos_reclassificacao.filter(
                    desclassificado_de="PCD"
                ).exists()
            ):
                # promovido de PCD para GERAL
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

    # Posições alvo (1-based) limitadas ao total
    # Posicionamento incremental: considerar offset dos já convocados,
    # mas gerar a sequência do novo lote no intervalo (offset, cumul_total]
    offset = convocados_total
    pcd_positions = []
    for i in range(1, cumul_pcd + 1):
        pos_abs = calcular_posicao_pcd(i)
        if offset < pos_abs <= cumul_total:
            pcd_positions.append(
                pos_abs - offset - 1
            )  # índice relativo ao novo lote
            if len(pcd_positions) >= pcd_total:
                break
    nna_positions = []
    for i in range(1, cumul_nna + 1):
        pos_abs = 3 if i == 1 and cumul_total >= 3 else calcular_posicao_nna(i)
        if offset < pos_abs <= cumul_total:
            nna_positions.append(
                pos_abs - offset - 1
            )  # índice relativo ao novo lote
            if len(nna_positions) >= nna_total:
                break

    # Verificação de reclassificados NNA: pega a maior classificacao_nna selecionada e,  # noqa: E501
    # se houver reclassificado de NNA com classificacao_nna menor, seta processo_uuid no histórico  # noqa: E501

    def place_at_or_next_free(index_list, label, remaining):
        placed = 0
        for idx in index_list:
            if placed >= remaining:
                break
            # tenta a posição alvo, senão avança até próxima vaga
            j = idx
            while j < total_convocados and sequencia[j] != "G":
                j += 1
            if j < total_convocados:
                sequencia[j] = label
                placed += 1
        return placed

    # Prioridade PCD em caso de colisão
    pcd_placed = place_at_or_next_free(pcd_positions, "PCD", pcd_total)
    nna_placed = place_at_or_next_free(nna_positions, "NNA", nna_total)

    # Se faltou posicionar algum (por posições > total, etc.), completa das esquerdas livres  # noqa: E501
    def backfill_remaining(label, remaining_to_place):
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

    # Monta a lista final de objetos com ranking baseado na posição
    resultado_itens = [None] * total_convocados

    def pop_from(label):
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
            # fallback simples para evitar buracos caso uma lista acabe
            if label != "NNA":
                item = pop_from("NNA")
            if item is None and label != "PCD":
                item = pop_from("PCD")
            if item is None and label != "G":
                item = pop_from("G")
        if item is not None:
            try:  # noqa: SIM105
                item.ranking = (
                    i + 1
                )  # não persiste; apenas atribui na instância
            except Exception:
                pass
            resultado_itens[i] = item

    final_itens = [it for it in resultado_itens if it is not None]
    with contextlib.suppress(Exception):
        [str(it.uuid) for it in final_itens]

    # Atualiza processo_uuid nos históricos de reclassificação relevantes (PCD e NNA)  # noqa: E501
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
    # Atualiza processo_uuid nos históricos de eliminação relevantes (todas classificações)  # noqa: E501
    _atualizar_processo_uuid_para_eliminados(
        final_itens=final_itens,
        processo_uuid=processo_uuid,
        lote=lote,
        codigo_cargo=codigo_cargo,
    )

    # Persiste o ranking com a posição final (1-based) para não ficar 0
    atualizar_ranking(final_itens)
    atualizar_ranking_escolha(final_itens)
    return final_itens, porcentagem_nna, porcentagem_pcd
