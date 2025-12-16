from candidatos.models import ConcursoCandidato


def atualizar_ranking(itens):
    try:
        for idx, it in enumerate(itens, start=1):
            it.ranking = idx
        if itens:
            ConcursoCandidato.objects.bulk_update(itens, ['ranking'])
    except Exception:
        # Em caso de erro de persistência, segue retornando os itens
        pass


def atualizar_ranking_escolha(itens):
    """
    Define ranking_escolha conforme regra:
    - Pegue todos os itens com classificacao_pcd preenchida e ordene-os por classificacao.
    - Os demais itens devem ser ordenados por classificacao (nulos por último).
    - Concatene: [pcd_ordenados_por_classificacao] + [demais_na_ordem_atual]
    - Atribua ranking_escolha = posição (1-based) nessa lista resultante.
    """
    try:
        # Itens com PCD (classificacao_pcd não nulo), ordenados por 'classificacao'
        itens_pcd = [it for it in itens if getattr(it, 'classificacao_pcd', None) is not None]
        itens_pcd.sort(key=lambda it: (getattr(it, 'classificacao', None) is None, getattr(it, 'classificacao', 0)))

        # Demais itens ordenados por 'classificacao' (nulos por último)
        itens_restantes = [it for it in itens if getattr(it, 'classificacao_pcd', None) is None]
        itens_restantes.sort(key=lambda it: (getattr(it, 'classificacao', None) is None, getattr(it, 'classificacao', float('inf'))))

        nova_ordem = itens_pcd + itens_restantes

        for idx, it in enumerate(nova_ordem, start=1):
            it.ranking_escolha = idx

        if nova_ordem:
            ConcursoCandidato.objects.bulk_update(nova_ordem, ['ranking_escolha'])
    except Exception:
        # Em caso de erro de persistência, segue retornando os itens
        pass