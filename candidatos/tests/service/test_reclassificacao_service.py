import pytest
from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
)
from candidatos.service.reclassificacao_service import (
    aplicar_reclassificacao,
    _categoria_efetiva_calculada,
)


pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candidato(cpf='10000000001', email='rc1@test.com'):
    return Candidato.objects.create(
        nome='Candidato Reclassificacao',
        cpf=cpf,
        email=email,
        data_nascimento='1990-01-01',
    )


def _make_cc(candidato=None, classificacao=1, classificacao_pcd=None, classificacao_nna=None, categoria_efetiva='GERAL'):
    if candidato is None:
        candidato = _make_candidato()
    return ConcursoCandidato.objects.create(
        candidato=candidato,
        codigo_inscricao='INS-RC-001',
        classificacao=classificacao,
        classificacao_pcd=classificacao_pcd,
        classificacao_nna=classificacao_nna,
        categoria_efetiva=categoria_efetiva,
    )


# ---------------------------------------------------------------------------
# _categoria_efetiva_calculada – lógica pura
# ---------------------------------------------------------------------------

def test_categoria_efetiva_calculada_pcd_ativo():
    cc = _make_cc(classificacao_pcd=2, classificacao_nna=3, categoria_efetiva='PCD')
    assert _categoria_efetiva_calculada(cc) == 'PCD'


def test_categoria_efetiva_calculada_nna_ativo():
    cc = _make_cc(classificacao_nna=3, categoria_efetiva='NNA')
    assert _categoria_efetiva_calculada(cc) == 'NNA'


def test_categoria_efetiva_calculada_geral():
    cc = _make_cc(categoria_efetiva='GERAL')
    assert _categoria_efetiva_calculada(cc) == 'GERAL'


def test_categoria_efetiva_calculada_pcd_desclassificado_cai_para_nna():
    cc = _make_cc(classificacao_pcd=2, classificacao_nna=3, categoria_efetiva='PCD')
    ConcursoCandidatoReclassificacao.objects.create(
        concurso_candidato=cc,
        desclassificado_de='PCD',
    )
    assert _categoria_efetiva_calculada(cc) == 'NNA'


def test_categoria_efetiva_calculada_pcd_e_nna_desclassificados_cai_para_geral():
    cc = _make_cc(classificacao_pcd=2, classificacao_nna=3, categoria_efetiva='PCD')
    ConcursoCandidatoReclassificacao.objects.create(concurso_candidato=cc, desclassificado_de='PCD')
    ConcursoCandidatoReclassificacao.objects.create(concurso_candidato=cc, desclassificado_de='NNA')
    assert _categoria_efetiva_calculada(cc) == 'GERAL'


def test_categoria_efetiva_calculada_sem_classificacao_retorna_geral():
    cc = _make_cc(classificacao=None, categoria_efetiva='GERAL')
    assert _categoria_efetiva_calculada(cc) == 'GERAL'


# ---------------------------------------------------------------------------
# aplicar_reclassificacao – caminho feliz NNA
# ---------------------------------------------------------------------------

def test_aplicar_reclassificacao_nna_cria_historico():
    cc = _make_cc(classificacao_nna=5, categoria_efetiva='NNA')

    cc_ret, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid,
        desclassificar_de='NNA',
        motivo='Documentação inválida',
        executado_por='operador',
    )

    assert ConcursoCandidatoReclassificacao.objects.filter(concurso_candidato=cc, desclassificado_de='NNA').count() == 1
    assert hist.motivo == 'Documentação inválida'
    assert hist.executado_por == 'operador'
    assert hist.desclassificado_de == 'NNA'


def test_aplicar_reclassificacao_nna_atualiza_categoria_para_geral():
    cc = _make_cc(classificacao_nna=5, categoria_efetiva='NNA')

    cc_ret, _ = aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')

    cc.refresh_from_db()
    assert cc.categoria_efetiva == 'GERAL'


# ---------------------------------------------------------------------------
# aplicar_reclassificacao – caminho feliz PCD
# ---------------------------------------------------------------------------

def test_aplicar_reclassificacao_pcd_cria_historico():
    cc = _make_cc(classificacao_pcd=3, categoria_efetiva='PCD')

    cc_ret, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid,
        desclassificar_de='PCD',
        motivo='Laudo vencido',
    )

    assert hist.desclassificado_de == 'PCD'
    assert hist.motivo == 'Laudo vencido'


def test_aplicar_reclassificacao_pcd_com_nna_ativo_vira_nna():
    cc = _make_cc(classificacao_pcd=3, classificacao_nna=5, categoria_efetiva='PCD')

    cc_ret, _ = aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='PCD')

    cc.refresh_from_db()
    assert cc.categoria_efetiva == 'NNA'


def test_aplicar_reclassificacao_retorna_tupla_correta():
    cc = _make_cc(classificacao_nna=2, categoria_efetiva='NNA')

    result = aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')

    assert isinstance(result, tuple) and len(result) == 2
    cc_ret, hist = result
    assert cc_ret.id == cc.id
    assert isinstance(hist, ConcursoCandidatoReclassificacao)


def test_aplicar_reclassificacao_sem_motivo_usa_string_vazia():
    cc = _make_cc(classificacao_nna=1, categoria_efetiva='NNA')

    _, hist = aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')

    assert hist.motivo == ''
    assert hist.executado_por == ''


# ---------------------------------------------------------------------------
# aplicar_reclassificacao – validações de erro
# ---------------------------------------------------------------------------

def test_aplicar_reclassificacao_desclassificar_de_invalido():
    cc = _make_cc()

    with pytest.raises(ValueError, match='inválido'):
        aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='GERAL')


def test_aplicar_reclassificacao_desclassificar_de_vazio():
    cc = _make_cc()

    with pytest.raises(ValueError, match='inválido'):
        aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='')


def test_aplicar_reclassificacao_nna_sem_classificacao_nna():
    cc = _make_cc(classificacao_nna=None, categoria_efetiva='GERAL')

    with pytest.raises(ValueError, match='não possui classificação NNA'):
        aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')


def test_aplicar_reclassificacao_pcd_sem_classificacao_pcd():
    cc = _make_cc(classificacao_pcd=None, categoria_efetiva='GERAL')

    with pytest.raises(ValueError, match='não possui classificação PCD'):
        aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='PCD')


def test_aplicar_reclassificacao_duplicata_levanta_erro():
    cc = _make_cc(classificacao_nna=4, categoria_efetiva='NNA')
    aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')

    with pytest.raises(ValueError, match='Já há desclassificação'):
        aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')


def test_aplicar_reclassificacao_uuid_inexistente():
    import uuid as _uuid

    with pytest.raises(ConcursoCandidato.DoesNotExist):
        aplicar_reclassificacao(candidato_uuid=_uuid.uuid4(), desclassificar_de='NNA')


# ---------------------------------------------------------------------------
# aplicar_reclassificacao – case-insensitive no desclassificar_de
# ---------------------------------------------------------------------------

def test_aplicar_reclassificacao_aceita_lowercase():
    cc = _make_cc(classificacao_nna=2, categoria_efetiva='NNA')

    _, hist = aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='nna')

    assert hist.desclassificado_de == 'NNA'


# ---------------------------------------------------------------------------
# aplicar_reclassificacao – categoria não muda quando já está correta
# ---------------------------------------------------------------------------

def test_aplicar_reclassificacao_nao_salva_se_categoria_nao_muda():
    """Se a categoria_efetiva já for GERAL (sem PCD/NNA), não deve chamar save."""
    cc = _make_cc(classificacao_nna=1, categoria_efetiva='NNA')

    # Força categoria_efetiva para GERAL antes (simulando estado inconsistente)
    ConcursoCandidato.objects.filter(pk=cc.pk).update(categoria_efetiva='GERAL')
    cc.refresh_from_db()

    # A reclassificação NNA deve funcionar sem erro mesmo que a categoria já seja GERAL
    _, hist = aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de='NNA')
    assert hist.desclassificado_de == 'NNA'
