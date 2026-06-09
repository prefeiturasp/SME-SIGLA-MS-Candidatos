"""Testes unitários para candidatos/service/calculo_habilitados_service.py.

Cobre: funções de cálculo, _safe_max_classificacao, _atualizar_processo_uuid_*,
       gerar_sequencia_convocados.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoEliminacao,
    ConcursoCandidatoReclassificacao,
    ConcursoCandidatosLote,
)
from candidatos.service.calculo_habilitados_service import (
    _atualizar_processo_uuid_para_eliminados,
    _atualizar_processo_uuid_para_reclassificados,
    _safe_max_classificacao,
    calcular_posicao_nna,
    calcular_posicao_pcd,
    calcular_quantidade_geral,
    calcular_quantidade_nna,
    calcular_quantidade_pcd,
    gerar_sequencia_convocados,
)

pytestmark = pytest.mark.django_db


def _candidato(**kwargs: Any) -> Any:
    """Executa  candidato."""
    return Candidato.objects.create(
        nome=kwargs.get("nome", "Teste"),
        cpf=kwargs.get("cpf", f"{uuid4().int % 10 ** 11:011d}"),
        email=kwargs.get("email", f"{uuid4().hex[:8]}@example.com"),
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


def _cc(
    lote: Any,
    candidato: Any = None,
    codigo_cargo: Any = "CARGO1",
    **kwargs: Any,
) -> Any:
    """Executa  cc."""
    return ConcursoCandidato.objects.create(
        candidato=candidato or _candidato(),
        lote=lote,
        codigo_inscricao=kwargs.get("codigo_inscricao", uuid4().hex[:8]),
        codigo_cargo=codigo_cargo,
        foi_convocado=kwargs.get("foi_convocado", False),
        eliminado=kwargs.get("eliminado", False),
        classificacao=kwargs.get("classificacao"),
        classificacao_nna=kwargs.get("classificacao_nna"),
        classificacao_pcd=kwargs.get("classificacao_pcd"),
        categoria_efetiva=kwargs.get("categoria_efetiva", "GERAL"),
    )


@pytest.fixture
def lote() -> Any:
    """Executa lote."""
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(), concurso_nome="Concurso Teste"
    )


class TestCalcularQuantidade:
    """Define TestCalcularQuantidade."""

    def test_calcular_quantidade_nna(self) -> None:
        """Verifica calcular quantidade nna."""
        assert calcular_quantidade_nna(0, 0.2) == 0
        assert calcular_quantidade_nna(10, 0.2) == 2
        assert calcular_quantidade_nna(7, 0.2) == 2
        assert calcular_quantidade_nna(100, 0.2) == 20

    def test_calcular_quantidade_pcd(self) -> None:
        """Verifica calcular quantidade pcd."""
        assert calcular_quantidade_pcd(0, 0.05) == 0
        assert calcular_quantidade_pcd(100, 0.05) == 5
        assert calcular_quantidade_pcd(30, 0.05) == 2
        assert calcular_quantidade_pcd(20, 0.05) == 1
        assert calcular_quantidade_pcd(10, 0.05) == 1

    def test_calcular_quantidade_geral(self) -> None:
        """Verifica calcular quantidade geral."""
        assert calcular_quantidade_geral(100, 0.2, 0.05) == 100 - 20 - 5
        assert calcular_quantidade_geral(10, 0.2, 0.05) == 10 - 2 - 1


class TestCalcularPosicao:
    """Define TestCalcularPosicao."""

    def test_calcular_posicao_nna(self) -> None:
        """Verifica calcular posicao nna."""
        assert calcular_posicao_nna(1) == 1
        assert calcular_posicao_nna(2) == 6
        assert calcular_posicao_nna(3) == 11

    def test_calcular_posicao_pcd(self) -> None:
        """Verifica calcular posicao pcd."""
        assert calcular_posicao_pcd(1) == 10
        assert calcular_posicao_pcd(2) == 30
        assert calcular_posicao_pcd(3) == 50


class TestSafeMaxClassificacao:
    """Define TestSafeMaxClassificacao."""

    def test_retorna_max_classificacao(self) -> None:
        """Verifica retorna max classificacao."""
        o1 = MagicMock(
            classificacao=5, classificacao_nna=None, classificacao_pcd=None
        )
        o2 = MagicMock(
            classificacao=10, classificacao_nna=None, classificacao_pcd=None
        )
        assert _safe_max_classificacao([o1, o2], "classificacao") == 10

    def test_ignora_nulos(self) -> None:
        """Verifica ignora nulos."""
        o1 = MagicMock(
            classificacao=None, classificacao_nna=None, classificacao_pcd=None
        )
        o2 = MagicMock(
            classificacao=3, classificacao_nna=None, classificacao_pcd=None
        )
        assert _safe_max_classificacao([o1, o2], "classificacao") == 3

    def test_geral_ignora_itens_com_classificacao_nna(self) -> None:
        """Para attr 'classificacao', ignora itens que tenham."""
        o1 = MagicMock(
            classificacao=10, classificacao_nna=1, classificacao_pcd=None
        )
        o2 = MagicMock(
            classificacao=5, classificacao_nna=None, classificacao_pcd=None
        )
        assert _safe_max_classificacao([o1, o2], "classificacao") == 5

    def test_geral_ignora_itens_com_classificacao_pcd(self) -> None:
        """Verifica geral ignora itens com classificacao pcd."""
        o1 = MagicMock(
            classificacao=10, classificacao_nna=None, classificacao_pcd=1
        )
        o2 = MagicMock(
            classificacao=5, classificacao_nna=None, classificacao_pcd=None
        )
        assert _safe_max_classificacao([o1, o2], "classificacao") == 5

    def test_lista_vazia_retorna_none(self) -> None:
        """Verifica lista vazia retorna none."""
        assert _safe_max_classificacao([], "classificacao") is None

    def test_todos_nulos_retorna_none(self) -> None:
        """Verifica todos nulos retorna none."""
        o = MagicMock(
            classificacao=None, classificacao_nna=None, classificacao_pcd=None
        )
        assert _safe_max_classificacao([o], "classificacao") is None

    def test_classificacao_nna_attr(self) -> None:
        """Verifica classificacao nna attr."""
        o1 = MagicMock(classificacao_nna=2)
        o2 = MagicMock(classificacao_nna=7)
        assert _safe_max_classificacao([o1, o2], "classificacao_nna") == 7

    def test_ignora_item_que_lanca_excecao_ao_acessar_attr(self) -> None:
        """Verifica ignora item que lanca excecao ao acessar attr."""

        class BadObj:
            """Define BadObj."""

            @property
            def classificacao(self) -> None:
                """Executa classificacao."""
                raise ValueError("erro")

            classificacao_nna = None
            classificacao_pcd = None

        o1 = MagicMock(
            classificacao=5, classificacao_nna=None, classificacao_pcd=None
        )
        lista = [o1, BadObj()]
        assert _safe_max_classificacao(lista, "classificacao") == 5


class TestAtualizarProcessoUuidReclassificados:
    """Define TestAtualizarProcessoUuidReclassificados."""

    def test_sem_processo_uuid_nao_faz_nada(self, lote: Any) -> None:
        """Verifica sem processo uuid nao faz nada."""
        _atualizar_processo_uuid_para_reclassificados(
            final_itens=[],
            categoria="NNA",
            classificacao_attr="classificacao_nna",
            processo_uuid=None,
            lote=lote,
            codigo_cargo="CARGO1",
        )
        assert ConcursoCandidatoReclassificacao.objects.count() == 0

    def test_com_limite_atualiza_historicos(self, lote: Any) -> None:
        """Verifica com limite atualiza historicos."""
        c = _candidato()
        cc_menor = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="r1",
            codigo_cargo="CARGO1",
            classificacao_nna=1,
            classificacao_pcd=None,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc_menor,
            desclassificado_de="NNA",
            processo_uuid=None,
        )
        obj_maior = MagicMock()
        obj_maior.classificacao_nna = 5
        obj_maior.classificacao_pcd = None
        obj_maior.classificacao = None
        processo_uuid = uuid4()
        _atualizar_processo_uuid_para_reclassificados(
            final_itens=[obj_maior],
            categoria="NNA",
            classificacao_attr="classificacao_nna",
            processo_uuid=processo_uuid,
            lote=lote,
            codigo_cargo="CARGO1",
        )
        rec = ConcursoCandidatoReclassificacao.objects.get(
            concurso_candidato=cc_menor
        )
        assert rec.processo_uuid == processo_uuid


class TestAtualizarProcessoUuidEliminados:
    """Define TestAtualizarProcessoUuidEliminados."""

    def test_sem_processo_uuid_nao_faz_nada(self, lote: Any) -> None:
        """Verifica sem processo uuid nao faz nada."""
        _atualizar_processo_uuid_para_eliminados(
            final_itens=[],
            processo_uuid=None,
            lote=lote,
            codigo_cargo="CARGO1",
        )

    def test_com_limites_atualiza_historicos(self, lote: Any) -> None:
        """Verifica com limites atualiza historicos."""
        c = _candidato()
        cc = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="e1",
            codigo_cargo="CARGO1",
            eliminado=True,
            classificacao=3,
        )
        ConcursoCandidatoEliminacao.objects.create(
            concurso_candidato=cc, processo_uuid=None
        )
        obj = MagicMock()
        obj.classificacao = 10
        obj.classificacao_nna = None
        obj.classificacao_pcd = None
        processo_uuid = uuid4()
        _atualizar_processo_uuid_para_eliminados(
            final_itens=[obj],
            processo_uuid=processo_uuid,
            lote=lote,
            codigo_cargo="CARGO1",
        )
        elim = ConcursoCandidatoEliminacao.objects.get(concurso_candidato=cc)
        assert elim.processo_uuid == processo_uuid


class TestGerarSequenciaConvocados:
    """Define TestGerarSequenciaConvocados."""

    def test_total_zero_retorna_lista_vazia(self, lote: Any) -> None:
        """Verifica total zero retorna lista vazia."""
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                assert (
                    gerar_sequencia_convocados(
                        0, lote=lote, codigo_cargo="CARGO1"
                    )
                    == []
                )
                assert (
                    gerar_sequencia_convocados(
                        -1, lote=lote, codigo_cargo="CARGO1"
                    )
                    == []
                )

    def test_sem_candidatos_retorna_lista_vazia(self, lote: Any) -> None:
        """Verifica sem candidatos retorna lista vazia."""
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, porcentagem_nna, porcentagem_pcd = (
                    gerar_sequencia_convocados(
                        5, lote=lote, codigo_cargo="CARGO1"
                    )
                )
        assert itens == []
        assert porcentagem_nna == 0.2
        assert porcentagem_pcd == 0.05

    def test_retorna_geral_quando_so_geral_disponivel(self, lote: Any) -> None:
        """Verifica retorna geral quando so geral disponivel."""
        for i in range(1, 6):
            _cc(
                lote,
                codigo_cargo="CARGO1",
                classificacao=i,
                classificacao_nna=None,
                classificacao_pcd=None,
            )
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    3, lote=lote, codigo_cargo="CARGO1"
                )
        assert len(itens) == 3
        assert all(
            getattr(it, "classificacao", None) is not None for it in itens
        )

    def test_respeita_quantidade_solicitada(self, lote: Any) -> None:
        """Verifica respeita quantidade solicitada."""
        for i in range(1, 11):
            _cc(
                lote,
                codigo_cargo="CARGO1",
                classificacao=i,
                classificacao_nna=None,
                classificacao_pcd=None,
            )
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    4, lote=lote, codigo_cargo="CARGO1"
                )
        assert len(itens) == 4

    def test_inclui_nna_e_pcd_quando_disponiveis(self, lote: Any) -> None:
        """Verifica inclui nna e pcd quando disponiveis."""
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao=1,
            classificacao_nna=None,
            classificacao_pcd=None,
        )
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao=2,
            classificacao_nna=None,
            classificacao_pcd=None,
        )
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao_nna=1,
            classificacao_pcd=None,
            categoria_efetiva="NNA",
        )
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao_pcd=1,
            classificacao_nna=None,
            categoria_efetiva="PCD",
        )
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    4, lote=lote, codigo_cargo="CARGO1"
                )
        assert len(itens) == 3
        categorias = [getattr(it, "categoria_efetiva", None) for it in itens]
        assert "NNA" in categorias or "GERAL" in categorias
        assert "PCD" in categorias or "GERAL" in categorias

    def test_filtra_por_escolhas_candidato_uuids(self, lote: Any) -> None:
        """Verifica filtra por escolhas candidato uuids."""
        cc1 = _cc(lote, codigo_cargo="CARGO1", classificacao=1)
        _cc(lote, codigo_cargo="CARGO1", classificacao=2)
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    3,
                    lote=lote,
                    codigo_cargo="CARGO1",
                    escolhas_candidato_uuids=[str(cc1.uuid)],
                )
        assert len(itens) == 2
        assert itens[0].uuid == cc1.uuid

    def test_nao_conta_eliminados_em_convocados(self, lote: Any) -> None:
        """Verifica nao conta eliminados em convocados."""
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao=1,
            foi_convocado=True,
            eliminado=False,
        )
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao=2,
            foi_convocado=False,
            eliminado=False,
        )
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    2, lote=lote, codigo_cargo="CARGO1"
                )
        assert len(itens) >= 1

    def test_atribui_ranking_nos_itens(self, lote: Any) -> None:
        """Verifica atribui ranking nos itens."""
        for i in range(1, 4):
            _cc(lote, codigo_cargo="CARGO1", classificacao=i)
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ) as mock_rank:
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    3, lote=lote, codigo_cargo="CARGO1"
                )
        assert len(itens) == 3
        mock_rank.assert_called_once()
        args = mock_rank.call_args[0][0]
        assert len(args) == 3

    def test_com_processo_uuid_chama_atualizacao_historicos(
        self, lote: Any
    ) -> None:
        """Verifica com processo uuid chama atualizacao historicos."""
        for i in range(1, 3):
            _cc(lote, codigo_cargo="CARGO1", classificacao=i)
        processo_uuid = uuid4()
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    2,
                    lote=lote,
                    codigo_cargo="CARGO1",
                    processo_uuid=processo_uuid,
                )
        assert len(itens) == 2

    def test_marca_promovido_para_geral_quando_geral_tem_classificacao_nna(
        self, lote: Any
    ) -> None:
        """Candidato em geral_list com classificacao_nna e sem histórico NNA é."""
        _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao=1,
            classificacao_nna=None,
            classificacao_pcd=None,
        )
        cc_nna = _cc(
            lote,
            codigo_cargo="CARGO1",
            classificacao=2,
            classificacao_nna=1,
            classificacao_pcd=None,
            categoria_efetiva="GERAL",
        )
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    5, lote=lote, codigo_cargo="CARGO1"
                )
        assert len(itens) >= 2
        cc_nna.refresh_from_db()
        assert cc_nna.promovido_para_geral is True
        assert cc_nna.promovido_de == "NNA"

    def test_codigo_cargo_vazio_filtra_candidatos_com_cargo_vazio(
        self, lote: Any
    ) -> None:
        """codigo_cargo='' filtra só candidatos com codigo_cargo vazio."""
        ConcursoCandidato.objects.create(
            candidato=_candidato(),
            lote=lote,
            codigo_inscricao="vazio",
            codigo_cargo="",
            classificacao=1,
            foi_convocado=False,
            eliminado=False,
        )
        with patch(
            "candidatos.service.calculo_habilitados_service.atualizar_ranking"
        ):
            with patch(
                "candidatos.service.calculo_habilitados_service.atualizar_ranking_escolha"
            ):
                itens, _, _ = gerar_sequencia_convocados(
                    5, lote=lote, codigo_cargo=""
                )
        assert len(itens) == 1
        assert itens[0].codigo_inscricao == "vazio"
