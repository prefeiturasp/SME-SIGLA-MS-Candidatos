"""Módulo service/candidato_service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from candidatos.models import Candidato, ConcursoCandidato
from candidatos.repository import (
    CandidatoRepository,
    ConcursoCandidatoRepository,
)
from candidatos.service.historico_classificacao_service import (
    registrar_deslocamento_classificacao,
)


def remover_mascara_cpf(cpf: str) -> str:
    """Remove máscara do CPF, retornando apenas os dígitos.

    Args:
        cpf: CPF com ou sem máscara (ex: "123.456.789-00" ou "12345678900").

    Returns:
        Conteúdo textual gerado.
    """
    if not cpf:
        return ""
    return "".join(filter(str.isdigit, str(cpf)))


def _none_if_empty(value: Any) -> Any:
    """Converta strings vazias em None para campos opcionais."""
    if value is None:
        return None
    try:
        return None if str(value).strip() == "" else value
    except Exception:
        return value


def _to_int_or_none(value: Any) -> int | None:
    """Converta valor para int ou None."""
    value = _none_if_empty(value)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _categoria_efetiva(classificacao_pcd: Any, classificacao_nna: Any) -> str:
    """Determina categoria efetiva a partir das classificações."""
    if classificacao_pcd is not None:
        return "PCD"
    if classificacao_nna is not None:
        return "NNA"
    return "GERAL"


def _campos_concurso_do_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Extrai campos de ConcursoCandidato a partir do payload."""
    classificacao_pcd = _to_int_or_none(data.get("classificacao_deficiente"))
    classificacao_nna = _to_int_or_none(data.get("classificacao_nna"))
    classificacao = _to_int_or_none(data.get("classificacao"))
    raw_pontos = _none_if_empty(data.get("pontos"))
    try:
        pontos = float(raw_pontos) if raw_pontos is not None else 0.0
    except (TypeError, ValueError):
        pontos = 0.0
    return {
        "codigo_inscricao": data.get("codigo_inscricao", ""),
        "classificacao": classificacao,
        "pontos": pontos,
        "classificacao_pcd": classificacao_pcd,
        "opcao_concurso": data.get("opcao_concurso", ""),
        "codigo_cargo": data.get("codigo_cargo", ""),
        "cota": data.get("cota", ""),
        "descricao_cargo": data.get("descricao_cargo", ""),
        "df": data.get("df", ""),
        "classificacao_nna": classificacao_nna,
        "ano_concurso": data.get("ano_concurso", ""),
        "observacao": data.get("observacao", ""),
        "categoria_efetiva": _categoria_efetiva(
            classificacao_pcd, classificacao_nna
        ),
    }


def _dados_candidato_do_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Extrai campos de Candidato a partir do payload."""
    uf = data.get("uf") or ""
    genero_map = {"1": "M", "2": "F"}
    genero = genero_map.get(data.get("sexo", ""), "")
    data_nasc = data.get("data_nascimento")
    if data_nasc:
        try:
            data_nasc = datetime.strptime(
                str(data_nasc).strip(), "%d/%m/%Y"
            ).date()
        except Exception:
            data_nasc = None
    return {
        "nome": data.get("nome", ""),
        "cpf": remover_mascara_cpf(data.get("cpf", "")),
        "email": data.get("email", ""),
        "telefone": data.get("telefone", ""),
        "celular": data.get("celular", ""),
        "rg": data.get("rg", ""),
        "registro_funcional": data.get("registro_funcional", ""),
        "vinculo": data.get("vinculo", ""),
        "data_nascimento": data_nasc or datetime(1900, 1, 1).date(),
        "genero": genero,
        "endereco": data.get("endereco", ""),
        "numero": data.get("numero", ""),
        "complemento": data.get("complemento", ""),
        "bairro": data.get("bairro", ""),
        "cidade": data.get("cidade", ""),
        "estado": uf,
        "cep": data.get("cep", ""),
    }


def _criar_candidato(data: dict[str, Any]) -> Candidato:
    """Cria candidato a partir do payload."""
    return CandidatoRepository.criar(**_dados_candidato_do_payload(data))


def _atualizar_candidato(
    candidato: Candidato, data: dict[str, Any]
) -> Candidato:
    """Atualiza dados pessoais do candidato e persiste."""
    campos = _dados_candidato_do_payload(data)
    # CPF não deve ser alterado na atualização.
    campos.pop("cpf", None)
    campos_atualizacao = list(campos.keys()) + ["atualizado_em"]
    for campo, valor in campos.items():
        setattr(candidato, campo, valor)
    CandidatoRepository.salvar(
        candidato, campos_atualizacao=campos_atualizacao
    )
    return candidato


def _obter_ou_criar_candidato(data: dict[str, Any]) -> Candidato:
    """Reutiliza candidato existente pelo CPF ou cria um novo."""
    cpf = remover_mascara_cpf(data.get("cpf", ""))
    existente = CandidatoRepository.obter_por_cpf(cpf) if cpf else None
    if existente is not None:
        return _atualizar_candidato(existente, data)
    return _criar_candidato(data)


def _atualizar_concurso_candidato(
    concurso: ConcursoCandidato,
    campos: dict[str, Any],
) -> ConcursoCandidato:
    """Atualiza campos do concurso candidato e persiste."""
    campos_atualizacao = list(campos.keys()) + ["atualizado_em"]
    for campo, valor in campos.items():
        setattr(concurso, campo, valor)
    ConcursoCandidatoRepository.salvar(
        concurso, campos_atualizacao=campos_atualizacao
    )
    return concurso


def upsert_candidato_e_concurso(
    data: dict[str, Any],
    *,
    concurso_uuid: Any = None,
    concurso_nome: str = "",
    mandado_judicial: bool | None = None,
) -> tuple[Candidato, ConcursoCandidato]:
    """Cria ou atualiza candidato e registro de concurso.

    A unicidade de ``ConcursoCandidato`` considera CPF + ``codigo_cargo`` +
    ``concurso_uuid``. Assim, o mesmo CPF no mesmo concurso com cargos
    diferentes gera registros distintos. Quando a chave já existir, atualiza
    os dados e, se alguma classificação piorar, grava histórico de
    deslocamento.

    Args:
        data: Payload do candidato/concurso.
        concurso_uuid: UUID do concurso (para localizar registro existente).
        concurso_nome: Nome do concurso (opcional).
        mandado_judicial: Flag opcional repassada ao histórico.

    Returns:
        Tupla com candidato e concurso candidato.
    """
    breakpoint()
    campos = _campos_concurso_do_payload(data)
    cpf = remover_mascara_cpf(data.get("cpf", ""))
    codigo_cargo = campos["codigo_cargo"]
    existente: ConcursoCandidato | None = None
    if concurso_uuid and cpf:
        existente = (
            ConcursoCandidatoRepository.obter_por_cpf_cargo_no_concurso(
                concurso_uuid, cpf, codigo_cargo
            )
        )

    if existente is not None:
        registrar_deslocamento_classificacao(
            existente,
            classificacao_nova=campos["classificacao"],
            classificacao_nna_nova=campos["classificacao_nna"],
            classificacao_pcd_nova=campos["classificacao_pcd"],
            mandado_judicial=mandado_judicial,
        )
        _atualizar_candidato(existente.candidato, data)
        if concurso_uuid:
            campos["concurso_uuid"] = concurso_uuid
        if concurso_nome:
            campos["concurso_nome"] = concurso_nome
        concurso = _atualizar_concurso_candidato(existente, campos)
        return (concurso.candidato, concurso)

    candidato = _obter_ou_criar_candidato(data)
    concurso = ConcursoCandidatoRepository.criar(
        candidato=candidato,
        concurso_uuid=concurso_uuid,
        concurso_nome=concurso_nome,
        **campos,
    )
    return (candidato, concurso)
