Regras de negócio
=================

Esta seção descreve as **regras que o sistema aplica automaticamente** — ou seja, o que pode e o que não pode acontecer no tratamento dos candidatos habilitados.

Habilitados e lotes do concurso
-------------------------------

O que é
~~~~~~~

Cada concurso possui uma lista de **habilitados**. Essa lista chega ao sistema em **lotes de importação**. Na prática, quase todas as operações (listagem, cálculo, convocação, extração de dados) usam o **último lote** importado daquele concurso — a versão mais recente da classificação.

Cada registro de habilitado guarda, entre outras informações:

- Dados da pessoa (nome, CPF, contato, registro funcional)
- Código de inscrição e classificações (ampla, PCD, NNA)
- Cargo / opção do concurso
- Se já foi convocado, eliminado ou promovido de cota
- Dados de lote SIGPEC, quando já importados

Categorias e cotas
------------------

Os candidatos são tratados em três categorias efetivas:

.. list-table:: Categorias
   :header-rows: 1
   :widths: 20 80

   * - Categoria
     - Significado
   * - **GERAL**
     - Ampla concorrência
   * - **PCD**
     - Pessoa com Deficiência
   * - **NNA**
     - Reserva (Negro / Não declarado / Amarelo)

Os percentuais padrão vêm da **Parametrização**:

- **PCD**: padrão de **5%** (0,05)
- **NNA**: padrão de **20%** (0,20)

Como as quantidades são calculadas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dado o total de candidatos a convocar:

1. Calcula-se a quantidade **NNA** (arredondamento para cima).
2. Calcula-se a quantidade **PCD** (se a parte decimal for 0,5 ou mais, sobe; senão, desce).
3. O restante fica para a **GERAL**.

Se não houver candidatos suficientes em NNA ou PCD, as vagas sobram para a ampla concorrência.

Ordem na sequência de convocação
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

O sistema monta uma **fila intercalada**, reservando posições típicas para cotas (por exemplo, intervalos próprios para NNA e PCD). Candidatos de cota com boa classificação na ampla podem ser **promovidos para GERAL** naquele cálculo — o sistema registra de onde vieram e quando isso ocorreu.

Convocação e desconvocação
--------------------------

Convocar
~~~~~~~~

Ao convocar, o sistema marca o candidato como **convocado**, registra a data e associa o **processo de convocação**. Só entram registros do **último lote** do concurso informado.

Desconvocar
~~~~~~~~~~~

Ao desconvocar, o sistema:

1. Remove a marcação de convocado, a data e o vínculo com o processo
2. Se for informado o **cargo**, solicita ao **Módulo Agenda** a remoção das agendas daquele processo e cargo

Cálculo de habilitados para o processo
--------------------------------------

Quando a SME pede uma quantidade de candidatos para um concurso, processo e cargo, o sistema:

1. Consulta a **Parametrização** de cotas
2. Consulta o **Módulo Escolhas** para saber quem já escolheu ou está em reconvocação (essas pessoas já “ocupam” cota)
3. Monta a sequência GERAL / PCD / NNA no último lote
4. Atualiza a ordem (ranking) de convocação e a ordem usada na escolha
5. Devolve a lista pronta para a convocação

Eliminação
----------

A eliminação tira o candidato do fluxo de próximas convocações.

Regras importantes:

- Só é possível eliminar quem **ainda não está eliminado**
- Ficam registrados motivo, quem executou e a data
- É gerado um **histórico** de eliminação, que pode ficar vinculado ao processo

Reclassificação
---------------

A reclassificação **retira** o candidato da cota **NNA** ou **PCD**, passando-o para a categoria efetiva recalculada (em geral, ampla concorrência).

Regras importantes:

- Só é possível desclassificar de NNA se o candidato **tiver classificação NNA**
- Só é possível desclassificar de PCD se o candidato **tiver classificação PCD**
- Não se registra duas vezes a mesma desclassificação da mesma cota (exceto quando há **mandado judicial**)
- A prioridade da categoria efetiva, após o histórico, é: PCD ativo → NNA ativo → GERAL

Mandado judicial
~~~~~~~~~~~~~~~~

Quando a operação é feita por **mandado judicial**, o sistema **reverte** a desclassificação anterior: o histórico é marcado e o candidato volta à categoria de origem (NNA ou PCD).

Reposição
---------

A reposição busca candidatos **ainda não convocados** no último lote (opcionalmente filtrando por cargo).

É possível pedir quantidades separadas de:

- Ampla (pela classificação geral)
- PCD
- NNA

Útil para completar vagas deixadas por desistências.

Reconvocação
------------

A reconvocação trabalha em conjunto com o **Módulo Escolhas**:

1. Busca quem está na situação de reconvocação
2. Cruza com candidatos **já convocados** do último lote (e cargo, se informado)
3. Ordena priorizando PCD → NNA → GERAL
4. Limita pela quantidade solicitada

Extração de dados
-----------------

A extração de indicadores considera sempre o **último lote** de cada concurso e pode informar:

- Quantidade de **habilitados** (total e por categoria)
- Quantidade de **convocados**
- Quantidade de **não convocados**

Com filtros por ano e processos, os números podem ser apresentados **quebrados por ano**.

Lotes SIGPEC
------------

A importação de lotes SIGPEC atualiza, no habilitado:

- Número do lote
- Código da empresa (SIGPEC)
- Número da vaga
- Chave do inscrito
- Registro funcional e vínculo da pessoa

Regras importantes:

- A busca do candidato é feita pela **inscrição** dentro do concurso
- Se algum inscrito **não for encontrado**, **nada é gravado** (tudo ou nada)
- Antes de gravar, o sistema zera os campos do mesmo número de lote já existentes naquele concurso

Parametrização de cotas
-----------------------

O app de parametrização guarda os percentuais padrão de **PCD** e **NNA** usados no cálculo de habilitados.

- Os valores padrão são **5% PCD** e **20% NNA**
- Podem ser consultados e atualizados pela API
- A criação de novos registros pela API de criação padrão não é o fluxo operacional esperado — o uso típico é manter o parâmetro vigente

Auditoria
---------

Alterações relevantes nos cadastros de candidatos são **registradas automaticamente** (quem alterou, quando e o que mudou), garantindo rastreabilidade para auditorias e consultas futuras.
