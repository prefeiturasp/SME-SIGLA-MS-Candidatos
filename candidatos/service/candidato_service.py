"""Módulo service/candidato_service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from candidatos.models import Candidato, ConcursoCandidato


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


def upsert_candidato_e_concurso(
    data: dict[str, Any],
) -> tuple[Candidato, ConcursoCandidato]:
    """Cria candidato e registro de concurso a partir dos dados recebidos.

    Args:
        data: Data.

    Returns:
        Tupla com os objetos criados ou atualizados.
    """
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
    candidato = Candidato.objects.create(
        nome=data.get("nome", ""),
        cpf=remover_mascara_cpf(data.get("cpf", "")),
        email=data.get("email", ""),
        telefone=data.get("telefone", ""),
        celular=data.get("celular", ""),
        rg=data.get("rg", ""),
        registro_funcional=data.get("registro_funcional", ""),
        vinculo=data.get("vinculo", ""),
        data_nascimento=data_nasc or datetime(1900, 1, 1).date(),
        genero=genero,
        endereco=data.get("endereco", ""),
        numero=data.get("numero", ""),
        complemento=data.get("complemento", ""),
        bairro=data.get("bairro", ""),
        cidade=data.get("cidade", ""),
        estado=uf,
        cep=data.get("cep", ""),
    )

    def _none_if_empty(value: Any) -> Any:
        """Converte strings vazias em None para campos opcionais."""
        if value is None:
            return None
        try:
            return None if str(value).strip() == "" else value
        except Exception:
            return value

    classificacao_pcd_val = _none_if_empty(
        data.get("classificacao_deficiente")
    )
    classificacao_nna_val = _none_if_empty(data.get("classificacao_nna"))
    if classificacao_pcd_val is not None:
        categoria_efetiva_val = "PCD"
    elif classificacao_nna_val is not None:
        categoria_efetiva_val = "NNA"
    else:
        categoria_efetiva_val = "GERAL"
    concurso = ConcursoCandidato.objects.create(
        candidato=candidato,
        codigo_inscricao=data.get("codigo_inscricao", ""),
        classificacao=_none_if_empty(data.get("classificacao")),
        pontos=data.get("pontos", ""),
        classificacao_pcd=classificacao_pcd_val,
        opcao_concurso=data.get("opcao_concurso", ""),
        codigo_cargo=data.get("codigo_cargo", ""),
        cota=data.get("cota", ""),
        descricao_cargo=data.get("descricao_cargo", ""),
        df=data.get("df", ""),
        classificacao_nna=classificacao_nna_val,
        ano_concurso=data.get("ano_concurso", ""),
        observacao=data.get("observacao", ""),
        categoria_efetiva=categoria_efetiva_val,
    )
    return (candidato, concurso)
