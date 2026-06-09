"""Testes unitários para o serviço de Reclassificação de Candidatos."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
    ConcursoCandidatosLote,
)
from candidatos.service.reclassificacao_service import (
    _categoria_efetiva_calculada,
    aplicar_reclassificacao,
)

pytestmark = pytest.mark.django_db


def _criar_candidato(nome: Any, cpf: Any, email: Any = None) -> Any:
    """Executa  criar candidato."""
    if email is None:
        email = f"user-{uuid4().hex[:8]}@example.com"
    return Candidato.objects.create(
        nome=nome,
        cpf=cpf,
        email=email,
        telefone="",
        data_nascimento="1990-01-01",
        genero="M",
        endereco="",
        cidade="",
        estado="",
        cep="",
        status="ativo",
        observacoes="",
    )


@pytest.fixture
def lote() -> Any:
    """Executa lote."""
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(), concurso_nome="Concurso Teste"
    )


@pytest.fixture
def cc_com_nna(lote: Any) -> Any:
    """ConcursoCandidato com classificação NNA (e geral)."""
    c = _criar_candidato("Candidato NNA", "111.111.111-11")
    return ConcursoCandidato.objects.create(
        candidato=c,
        lote=lote,
        codigo_inscricao="001",
        classificacao=10,
        classificacao_nna=1,
        classificacao_pcd=None,
        categoria_efetiva="NNA",
    )


@pytest.fixture
def cc_com_pcd(lote: Any) -> Any:
    """ConcursoCandidato com classificação PCD (e geral)."""
    c = _criar_candidato("Candidato PCD", "222.222.222-22")
    return ConcursoCandidato.objects.create(
        candidato=c,
        lote=lote,
        codigo_inscricao="002",
        classificacao=20,
        classificacao_nna=None,
        classificacao_pcd=1,
        categoria_efetiva="PCD",
    )


@pytest.fixture
def cc_com_nna_e_pcd(lote: Any) -> Any:
    """ConcursoCandidato com classificação NNA e PCD."""
    c = _criar_candidato("Candidato NNA e PCD", "333.333.333-33")
    return ConcursoCandidato.objects.create(
        candidato=c,
        lote=lote,
        codigo_inscricao="003",
        classificacao=30,
        classificacao_nna=2,
        classificacao_pcd=2,
        categoria_efetiva="PCD",
    )


class TestAplicarReclassificacao:
    """Testes para aplicar_reclassificacao."""

    def test_reclassificar_de_nna_atualiza_categoria_efetiva_para_geral(
        self, cc_com_nna: Any
    ) -> None:
        """Verifica reclassificar de nna atualiza categoria efetiva para geral."""
        cc, hist = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna.uuid),
            desclassificar_de="NNA",
            motivo="Reclassificação solicitada",
            executado_por="usuario_teste",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"
        assert hist.desclassificado_de == "NNA"
        assert hist.motivo == "Reclassificação solicitada"
        assert hist.executado_por == "usuario_teste"
        assert cc.historicos_reclassificacao.filter(
            desclassificado_de="NNA"
        ).exists()

    def test_reclassificar_de_pcd_atualiza_categoria_efetiva_para_geral(
        self, cc_com_pcd: Any
    ) -> None:
        """Verifica reclassificar de pcd atualiza categoria efetiva para geral."""
        cc, hist = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_pcd.uuid),
            desclassificar_de="PCD",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"
        assert hist.desclassificado_de == "PCD"
        assert cc.historicos_reclassificacao.filter(
            desclassificado_de="PCD"
        ).exists()

    def test_reclassificar_aceita_desclassificar_de_minusculo(
        self, cc_com_nna: Any
    ) -> None:
        """Verifica reclassificar aceita desclassificar de minusculo."""
        cc, _ = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna.uuid),
            desclassificar_de="nna",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"

    def test_reclassificar_concurso_candidato_inexistente_levanta_does_not_exist(  # noqa: E501
        self,
    ) -> None:
        """Verifica reclassificar concurso candidato inexistente levanta does."""
        with pytest.raises(ConcursoCandidato.DoesNotExist):
            aplicar_reclassificacao(
                candidato_uuid=str(uuid4()),
                desclassificar_de="NNA",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_desclassificar_de_invalido_levanta_value_error(
        self, cc_com_nna: Any
    ) -> None:
        """Verifica reclassificar desclassificar de invalido levanta value."""
        with pytest.raises(ValueError, match="desclassificar_de inválido"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_nna.uuid),
                desclassificar_de="INVALIDO",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_sem_classificacao_nna_levanta_value_error(
        self, cc_com_pcd: Any
    ) -> None:
        """Verifica reclassificar sem classificacao nna levanta value error."""
        with pytest.raises(ValueError, match="não possui classificação NNA"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_pcd.uuid),
                desclassificar_de="NNA",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_sem_classificacao_pcd_levanta_value_error(
        self, cc_com_nna: Any
    ) -> None:
        """Verifica reclassificar sem classificacao pcd levanta value error."""
        with pytest.raises(ValueError, match="não possui classificação PCD"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_nna.uuid),
                desclassificar_de="PCD",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_duplicado_para_mesma_cota_levanta_value_error(
        self, cc_com_nna: Any
    ) -> None:
        """Verifica reclassificar duplicado para mesma cota levanta value."""
        aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        with pytest.raises(
            ValueError, match="Já há desclassificação registrada para NNA"
        ):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_nna.uuid),
                desclassificar_de="NNA",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_nna_e_depois_pcd_em_candidato_com_ambas(
        self, cc_com_nna_e_pcd: Any
    ) -> None:
        """Verifica reclassificar nna e depois pcd em candidato com ambas."""
        cc = cc_com_nna_e_pcd
        cc, hist1 = aplicar_reclassificacao(
            candidato_uuid=str(cc.uuid),
            desclassificar_de="PCD",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "NNA"
        assert (
            ConcursoCandidatoReclassificacao.objects.filter(
                concurso_candidato=cc
            ).count()
            == 1
        )
        cc, hist2 = aplicar_reclassificacao(
            candidato_uuid=str(cc.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"
        assert (
            ConcursoCandidatoReclassificacao.objects.filter(
                concurso_candidato=cc
            ).count()
            == 2
        )

    def test_campos_classificacao_originais_nao_sao_alterados(
        self, cc_com_nna: Any
    ) -> None:
        """Verifica campos classificacao originais nao sao alterados."""
        classificacao_antes = cc_com_nna.classificacao
        classificacao_nna_antes = cc_com_nna.classificacao_nna
        aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        cc_com_nna.refresh_from_db()
        assert cc_com_nna.classificacao == classificacao_antes
        assert cc_com_nna.classificacao_nna == classificacao_nna_antes

    def test_reclassificar_de_nna_em_candidato_com_nna_e_pcd_atualiza_para_pcd(
        self, cc_com_nna_e_pcd: Any
    ) -> None:
        """Desclassificar de NNA mantém PCD ativo -> categoria_efetiva vira."""
        cc, _ = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna_e_pcd.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "PCD"

    def test_reclassificar_candidato_so_nna_sem_geral_atualiza_para_geral(
        self, lote: Any
    ) -> None:
        """Candidato só com classificacao_nna (sem classificacao geral) ->."""
        c = _criar_candidato("Só NNA", "999.999.999-99")
        cc = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="só-nna",
            classificacao=None,
            classificacao_nna=1,
            classificacao_pcd=None,
            categoria_efetiva="NNA",
        )
        cc, _ = aplicar_reclassificacao(
            candidato_uuid=str(cc.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"


def _make_candidato(
    cpf: Any = "10000000001", email: Any = "rc1@test.com"
) -> Any:
    """Executa  make candidato."""
    return Candidato.objects.create(
        nome="Candidato Reclassificacao",
        cpf=cpf,
        email=email,
        data_nascimento="1990-01-01",
    )


def _make_cc(
    candidato: Any = None,
    classificacao: Any = 1,
    classificacao_pcd: Any = None,
    classificacao_nna: Any = None,
    categoria_efetiva: Any = "GERAL",
) -> Any:
    """Executa  make cc."""
    if candidato is None:
        candidato = _make_candidato()
    return ConcursoCandidato.objects.create(
        candidato=candidato,
        codigo_inscricao="INS-RC-001",
        classificacao=classificacao,
        classificacao_pcd=classificacao_pcd,
        classificacao_nna=classificacao_nna,
        categoria_efetiva=categoria_efetiva,
    )


def test_categoria_efetiva_calculada_pcd_ativo() -> None:
    """Verifica categoria efetiva calculada pcd ativo."""
    cc = _make_cc(
        classificacao_pcd=2, classificacao_nna=3, categoria_efetiva="PCD"
    )
    assert _categoria_efetiva_calculada(cc) == "PCD"


def test_categoria_efetiva_calculada_nna_ativo() -> None:
    """Verifica categoria efetiva calculada nna ativo."""
    cc = _make_cc(classificacao_nna=3, categoria_efetiva="NNA")
    assert _categoria_efetiva_calculada(cc) == "NNA"


def test_categoria_efetiva_calculada_geral() -> None:
    """Verifica categoria efetiva calculada geral."""
    cc = _make_cc(categoria_efetiva="GERAL")
    assert _categoria_efetiva_calculada(cc) == "GERAL"


def test_categoria_efetiva_calculada_pcd_desclassificado_cai_para_nna() -> (
    None
):
    """Verifica categoria efetiva calculada pcd desclassificado cai para nna."""
    cc = _make_cc(
        classificacao_pcd=2, classificacao_nna=3, categoria_efetiva="PCD"
    )
    ConcursoCandidatoReclassificacao.objects.create(
        concurso_candidato=cc, desclassificado_de="PCD"
    )
    assert _categoria_efetiva_calculada(cc) == "NNA"


def test_categoria_efetiva_calculada_pcd_e_nna_desclassificados_cai_para_geral() -> (  # noqa: E501
    None
):
    """Verifica categoria efetiva calculada pcd e nna desclassificados cai."""
    cc = _make_cc(
        classificacao_pcd=2, classificacao_nna=3, categoria_efetiva="PCD"
    )
    ConcursoCandidatoReclassificacao.objects.create(
        concurso_candidato=cc, desclassificado_de="PCD"
    )
    ConcursoCandidatoReclassificacao.objects.create(
        concurso_candidato=cc, desclassificado_de="NNA"
    )
    assert _categoria_efetiva_calculada(cc) == "GERAL"


def test_categoria_efetiva_calculada_sem_classificacao_retorna_geral() -> None:
    """Verifica categoria efetiva calculada sem classificacao retorna geral."""
    cc = _make_cc(classificacao=None, categoria_efetiva="GERAL")
    assert _categoria_efetiva_calculada(cc) == "GERAL"


def test_aplicar_reclassificacao_nna_cria_historico() -> None:
    """Verifica aplicar reclassificacao nna cria historico."""
    cc = _make_cc(classificacao_nna=5, categoria_efetiva="NNA")
    cc_ret, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid,
        desclassificar_de="NNA",
        motivo="Documentação inválida",
        executado_por="operador",
    )
    assert (
        ConcursoCandidatoReclassificacao.objects.filter(
            concurso_candidato=cc, desclassificado_de="NNA"
        ).count()
        == 1
    )
    assert hist.motivo == "Documentação inválida"
    assert hist.executado_por == "operador"
    assert hist.desclassificado_de == "NNA"


def test_aplicar_reclassificacao_nna_atualiza_categoria_para_geral() -> None:
    """Verifica aplicar reclassificacao nna atualiza categoria para geral."""
    cc = _make_cc(classificacao_nna=5, categoria_efetiva="NNA")
    cc_ret, _ = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="NNA"
    )
    cc.refresh_from_db()
    assert cc.categoria_efetiva == "GERAL"


def test_aplicar_reclassificacao_pcd_cria_historico() -> None:
    """Verifica aplicar reclassificacao pcd cria historico."""
    cc = _make_cc(classificacao_pcd=3, categoria_efetiva="PCD")
    cc_ret, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="PCD", motivo="Laudo vencido"
    )
    assert hist.desclassificado_de == "PCD"
    assert hist.motivo == "Laudo vencido"


def test_aplicar_reclassificacao_pcd_com_nna_ativo_vira_nna() -> None:
    """Verifica aplicar reclassificacao pcd com nna ativo vira nna."""
    cc = _make_cc(
        classificacao_pcd=3, classificacao_nna=5, categoria_efetiva="PCD"
    )
    cc_ret, _ = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="PCD"
    )
    cc.refresh_from_db()
    assert cc.categoria_efetiva == "NNA"


def test_aplicar_reclassificacao_retorna_tupla_correta() -> None:
    """Verifica aplicar reclassificacao retorna tupla correta."""
    cc = _make_cc(classificacao_nna=2, categoria_efetiva="NNA")
    result = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="NNA"
    )
    assert isinstance(result, tuple) and len(result) == 2
    cc_ret, hist = result
    assert cc_ret.id == cc.id
    assert isinstance(hist, ConcursoCandidatoReclassificacao)


def test_aplicar_reclassificacao_sem_motivo_usa_string_vazia() -> None:
    """Verifica aplicar reclassificacao sem motivo usa string vazia."""
    cc = _make_cc(classificacao_nna=1, categoria_efetiva="NNA")
    _, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="NNA"
    )
    assert hist.motivo == ""
    assert hist.executado_por == ""


def test_aplicar_reclassificacao_desclassificar_de_invalido() -> None:
    """Verifica aplicar reclassificacao desclassificar de invalido."""
    cc = _make_cc()
    with pytest.raises(ValueError, match="inválido"):
        aplicar_reclassificacao(
            candidato_uuid=cc.uuid, desclassificar_de="GERAL"
        )


def test_aplicar_reclassificacao_desclassificar_de_vazio() -> None:
    """Verifica aplicar reclassificacao desclassificar de vazio."""
    cc = _make_cc()
    with pytest.raises(ValueError, match="inválido"):
        aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de="")


def test_aplicar_reclassificacao_nna_sem_classificacao_nna() -> None:
    """Verifica aplicar reclassificacao nna sem classificacao nna."""
    cc = _make_cc(classificacao_nna=None, categoria_efetiva="GERAL")
    with pytest.raises(ValueError, match="não possui classificação NNA"):
        aplicar_reclassificacao(
            candidato_uuid=cc.uuid, desclassificar_de="NNA"
        )


def test_aplicar_reclassificacao_pcd_sem_classificacao_pcd() -> None:
    """Verifica aplicar reclassificacao pcd sem classificacao pcd."""
    cc = _make_cc(classificacao_pcd=None, categoria_efetiva="GERAL")
    with pytest.raises(ValueError, match="não possui classificação PCD"):
        aplicar_reclassificacao(
            candidato_uuid=cc.uuid, desclassificar_de="PCD"
        )


def test_aplicar_reclassificacao_duplicata_levanta_erro() -> None:
    """Verifica aplicar reclassificacao duplicata levanta erro."""
    cc = _make_cc(classificacao_nna=4, categoria_efetiva="NNA")
    aplicar_reclassificacao(candidato_uuid=cc.uuid, desclassificar_de="NNA")
    with pytest.raises(ValueError, match="Já há desclassificação"):
        aplicar_reclassificacao(
            candidato_uuid=cc.uuid, desclassificar_de="NNA"
        )


def test_aplicar_reclassificacao_uuid_inexistente() -> None:
    """Verifica aplicar reclassificacao uuid inexistente."""
    import uuid as _uuid

    with pytest.raises(ConcursoCandidato.DoesNotExist):
        aplicar_reclassificacao(
            candidato_uuid=_uuid.uuid4(), desclassificar_de="NNA"
        )


def test_aplicar_reclassificacao_aceita_lowercase() -> None:
    """Verifica aplicar reclassificacao aceita lowercase."""
    cc = _make_cc(classificacao_nna=2, categoria_efetiva="NNA")
    _, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="nna"
    )
    assert hist.desclassificado_de == "NNA"


def test_aplicar_reclassificacao_nao_salva_se_categoria_nao_muda() -> None:
    """Não chama save se categoria_efetiva já é GERAL (sem PCD/NNA)."""
    cc = _make_cc(classificacao_nna=1, categoria_efetiva="NNA")
    ConcursoCandidato.objects.filter(pk=cc.pk).update(
        categoria_efetiva="GERAL"
    )
    cc.refresh_from_db()
    _, hist = aplicar_reclassificacao(
        candidato_uuid=cc.uuid, desclassificar_de="NNA"
    )
    assert hist.desclassificado_de == "NNA"
