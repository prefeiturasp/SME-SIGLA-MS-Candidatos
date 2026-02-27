"""
Testes unitários para o serviço de Reclassificação de Candidatos habilitados.
"""
import pytest
from uuid import uuid4

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
    ConcursoCandidatoReclassificacao,
)
from candidatos.service.reclassificacao_service import aplicar_reclassificacao


pytestmark = pytest.mark.django_db


def _criar_candidato(nome, cpf, email=None):
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
def lote():
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome="Concurso Teste",
    )


@pytest.fixture
def cc_com_nna(lote):
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
def cc_com_pcd(lote):
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
def cc_com_nna_e_pcd(lote):
    """ConcursoCandidato com classificação NNA e PCD."""
    c = _criar_candidato("Candidato NNA e PCD", "333.333.333-33")
    return ConcursoCandidato.objects.create(
        candidato=c,
        lote=lote,
        codigo_inscricao="003",
        classificacao=30,
        classificacao_nna=2,
        classificacao_pcd=2,
        categoria_efetiva="PCD",  # PCD tem prioridade
    )


class TestAplicarReclassificacao:
    """Testes para aplicar_reclassificacao."""

    def test_reclassificar_de_nna_atualiza_categoria_efetiva_para_geral(self, cc_com_nna):
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
        assert cc.historicos_reclassificacao.filter(desclassificado_de="NNA").exists()

    def test_reclassificar_de_pcd_atualiza_categoria_efetiva_para_geral(self, cc_com_pcd):
        cc, hist = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_pcd.uuid),
            desclassificar_de="PCD",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"
        assert hist.desclassificado_de == "PCD"
        assert cc.historicos_reclassificacao.filter(desclassificado_de="PCD").exists()

    def test_reclassificar_aceita_desclassificar_de_minusculo(self, cc_com_nna):
        cc, _ = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna.uuid),
            desclassificar_de="nna",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"

    def test_reclassificar_concurso_candidato_inexistente_levanta_does_not_exist(self):
        with pytest.raises(ConcursoCandidato.DoesNotExist):
            aplicar_reclassificacao(
                candidato_uuid=str(uuid4()),
                desclassificar_de="NNA",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_desclassificar_de_invalido_levanta_value_error(self, cc_com_nna):
        with pytest.raises(ValueError, match="desclassificar_de inválido"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_nna.uuid),
                desclassificar_de="INVALIDO",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_sem_classificacao_nna_levanta_value_error(self, cc_com_pcd):
        with pytest.raises(ValueError, match="não possui classificação NNA"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_pcd.uuid),
                desclassificar_de="NNA",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_sem_classificacao_pcd_levanta_value_error(self, cc_com_nna):
        with pytest.raises(ValueError, match="não possui classificação PCD"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_nna.uuid),
                desclassificar_de="PCD",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_duplicado_para_mesma_cota_levanta_value_error(self, cc_com_nna):
        aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        with pytest.raises(ValueError, match="Já há desclassificação registrada para NNA"):
            aplicar_reclassificacao(
                candidato_uuid=str(cc_com_nna.uuid),
                desclassificar_de="NNA",
                motivo="",
                executado_por="",
            )

    def test_reclassificar_nna_e_depois_pcd_em_candidato_com_ambas(self, cc_com_nna_e_pcd):
        cc = cc_com_nna_e_pcd
        # Primeiro desclassifica de PCD -> categoria vira NNA (pois ainda tem NNA)
        cc, hist1 = aplicar_reclassificacao(
            candidato_uuid=str(cc.uuid),
            desclassificar_de="PCD",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "NNA"
        assert ConcursoCandidatoReclassificacao.objects.filter(concurso_candidato=cc).count() == 1

        # Depois desclassifica de NNA -> categoria vira GERAL
        cc, hist2 = aplicar_reclassificacao(
            candidato_uuid=str(cc.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"
        assert ConcursoCandidatoReclassificacao.objects.filter(concurso_candidato=cc).count() == 2

    def test_campos_classificacao_originais_nao_sao_alterados(self, cc_com_nna):
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

    def test_reclassificar_de_nna_em_candidato_com_nna_e_pcd_atualiza_para_pcd(self, cc_com_nna_e_pcd):
        """Desclassificar de NNA mantém PCD ativo -> categoria_efetiva vira PCD (cobre return PCD)."""
        cc, _ = aplicar_reclassificacao(
            candidato_uuid=str(cc_com_nna_e_pcd.uuid),
            desclassificar_de="NNA",
            motivo="",
            executado_por="",
        )
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "PCD"

    def test_reclassificar_candidato_so_nna_sem_geral_atualiza_para_geral(self, lote):
        """Candidato só com classificacao_nna (sem classificacao geral) -> fallback GERAL (cobre return GERAL final)."""
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
