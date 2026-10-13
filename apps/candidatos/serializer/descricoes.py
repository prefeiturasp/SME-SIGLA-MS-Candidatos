"""Descrições dos campos publicados na documentação da API."""

from typing import Any

DescricoesCampos = dict[str, dict[str, Any]]

DESCRICOES_REGISTRO: DescricoesCampos = {
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última atualização do registro."
    },
    "esta_ativo": {"help_text": "Indica se o registro está ativo."},
}

DESCRICOES_CANDIDATO: DescricoesCampos = {
    **DESCRICOES_REGISTRO,
    "id": {"help_text": "Identificador numérico interno do candidato."},
    "uuid": {"help_text": "Identificador único do candidato."},
    "nome": {"help_text": "Nome completo do candidato."},
    "cpf": {
        "help_text": (
            "CPF do candidato. A carga em lote grava apenas os dígitos."
        )
    },
    "email": {"help_text": "E-mail de contato."},
    "telefone": {"help_text": "Telefone fixo."},
    "celular": {"help_text": "Telefone celular."},
    "rg": {"help_text": "Número do RG."},
    "registro_funcional": {
        "help_text": (
            "Registro funcional (RF) do candidato que já é servidor. "
            "Atualizado ao salvar os lotes do SIGPEC."
        )
    },
    "vinculo": {
        "help_text": (
            "Número do vínculo funcional do servidor. Atualizado ao salvar "
            "os lotes do SIGPEC."
        )
    },
    "data_nascimento": {"help_text": "Data de nascimento."},
    "genero": {"help_text": "Gênero do candidato. Vazio se não informado."},
    "endereco": {"help_text": "Logradouro do endereço."},
    "numero": {"help_text": "Número do endereço."},
    "complemento": {"help_text": "Complemento do endereço."},
    "bairro": {"help_text": "Bairro do endereço."},
    "cidade": {"help_text": "Cidade do endereço."},
    "estado": {"help_text": "Sigla da unidade federativa, com 2 letras."},
    "cep": {"help_text": "CEP do endereço."},
    "status": {"help_text": "Situação do cadastro do candidato."},
    "observacoes": {"help_text": "Observações livres sobre o candidato."},
}

DESCRICOES_HABILITADO: DescricoesCampos = {
    **DESCRICOES_REGISTRO,
    "id": {
        "help_text": (
            "Identificador numérico interno do habilitado. É o valor usado "
            "nas rotas legadas `/habilitados/{id}/`."
        )
    },
    "uuid": {
        "help_text": (
            "Identificador único do habilitado. É o valor que as demais "
            "operações e os outros microsserviços chamam de "
            "`candidato_uuid`."
        )
    },
    "concurso_uuid": {"help_text": "UUID do concurso (MS-Concursos)."},
    "concurso_nome": {"help_text": "Nome do concurso."},
    "codigo_inscricao": {
        "help_text": "Código de inscrição do candidato no concurso."
    },
    "pontos": {"help_text": "Pontuação obtida no concurso."},
    "opcao_concurso": {
        "help_text": "Opção de concurso informada na inscrição."
    },
    "codigo_cargo": {"help_text": "Código do cargo."},
    "processo_uuid": {
        "help_text": (
            "UUID do processo de convocação (MS-ProcessosConvocacao) em que "
            "o habilitado foi convocado. Nulo enquanto não convocado."
        )
    },
    "cota": {"help_text": "Cota informada na inscrição."},
    "descricao_cargo": {"help_text": "Nome do cargo."},
    "df": {
        "help_text": (
            "Campo `DF` da lista de classificação do concurso, gravado como "
            "recebido."
        )
    },
    "classificacao": {"help_text": "Classificação na lista geral."},
    "classificacao_pcd": {
        "help_text": (
            "Classificação na lista PCD. Nulo se o habilitado não concorre "
            "nessa lista."
        )
    },
    "classificacao_nna": {
        "help_text": (
            "Classificação na lista NNA. Nulo se o habilitado não concorre "
            "nessa lista."
        )
    },
    "ano_concurso": {"help_text": "Ano do concurso."},
    "observacao": {"help_text": "Observações da inscrição."},
    "foi_convocado": {
        "help_text": "Indica se o habilitado está convocado em um processo."
    },
    "data_convocacao": {
        "help_text": (
            "Data e hora em que a convocação foi registrada. Nulo enquanto "
            "não convocado."
        )
    },
    "mandado_judicial": {
        "help_text": (
            "Indica que o habilitado entrou na lista por mandado judicial, "
            "isto é, em carga posterior à primeira do concurso."
        )
    },
    "ranking": {
        "help_text": (
            "Posição do habilitado na última sequência de convocação "
            "calculada (cálculo, reposição ou reconvocação)."
        )
    },
    "ranking_escolha": {
        "help_text": (
            "Ordem de escolha de vaga na última sequência calculada: "
            "primeiro quem concorre na lista PCD, depois os demais, sempre "
            "pela classificação geral."
        )
    },
    "categoria_efetiva": {
        "help_text": "Lista pela qual o habilitado é convocado."
    },
    "promovido_para_geral": {
        "help_text": (
            "Indica que o habilitado concorre em lista reservada, mas foi "
            "alcançado pela classificação geral no último cálculo de "
            "convocação."
        )
    },
    "promovido_de": {
        "help_text": (
            "Lista reservada de origem do habilitado promovido para a "
            "lista geral. Nulo se não houve promoção."
        )
    },
    "promovido_em": {
        "help_text": (
            "Data e hora da promoção para a lista geral. Nulo se não houve "
            "promoção."
        )
    },
    "eliminado": {"help_text": "Indica se o habilitado foi eliminado."},
    "eliminado_em": {
        "help_text": "Data e hora da eliminação. Nulo se não eliminado."
    },
    "eliminado_motivo": {"help_text": "Motivo informado na eliminação."},
    "eliminado_por": {
        "help_text": (
            "Usuário que registrou a eliminação. Vazio quando a chamada "
            "não foi autenticada."
        )
    },
    "numero_lote": {
        "help_text": (
            "Número do lote do SIGPEC. Nulo enquanto o lote não é salvo."
        )
    },
    "codigo_sigpec": {
        "help_text": (
            "Código da empresa no SIGPEC. Nulo enquanto o lote não é salvo."
        )
    },
    "numero_vaga": {
        "help_text": (
            "Número da vaga no SIGPEC. Nulo enquanto o lote não é salvo."
        )
    },
    "chave_inscrito": {
        "help_text": (
            "Chave do inscrito no SIGPEC. Nulo quando o lote não a traz."
        )
    },
}

DESCRICOES_HISTORICO_CLASSIFICACAO: DescricoesCampos = {
    "uuid": {"help_text": "Identificador único do registro de histórico."},
    "classificacao_anterior": {
        "help_text": "Classificação na lista geral antes da nova carga."
    },
    "classificacao_nova": {
        "help_text": "Classificação na lista geral depois da nova carga."
    },
    "classificacao_nna_anterior": {
        "help_text": "Classificação na lista NNA antes da nova carga."
    },
    "classificacao_nna_nova": {
        "help_text": "Classificação na lista NNA depois da nova carga."
    },
    "classificacao_pcd_anterior": {
        "help_text": "Classificação na lista PCD antes da nova carga."
    },
    "classificacao_pcd_nova": {
        "help_text": "Classificação na lista PCD depois da nova carga."
    },
    "foi_convocado": {
        "help_text": (
            "Indica se o habilitado já estava convocado quando a "
            "classificação mudou."
        )
    },
    "motivo": {"help_text": "Motivo ou observação da mudança."},
    "criado_em": {"help_text": "Data e hora em que a mudança foi registrada."},
}
