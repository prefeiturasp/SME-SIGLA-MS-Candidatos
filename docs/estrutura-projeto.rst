Estrutura do projeto
====================

Esta seção explica **cada pasta do repositório** e o papel de cada módulo dentro de ``apps/``.

Visão da árvore principal
-------------------------

.. code-block:: text

   ms-candidatos/
   ├── apps/              # Módulos de negócio (Django apps)
   ├── config/            # Configurações do projeto Django
   ├── docs/              # Documentação Sphinx (este material)
   ├── requirements/      # Dependências Python por ambiente
   ├── manage.py          # Ponto de entrada do Django
   ├── Dockerfile         # Imagem Docker da API
   ├── docker-compose.yml # Ambiente local
   └── Makefile           # Comandos úteis de desenvolvimento

Pasta ``apps/``
---------------

É onde ficam os **módulos de negócio**. Cada subpasta é um "app" Django com responsabilidade bem definida.

``apps/candidatos/``
~~~~~~~~~~~~~~~~~~~~

**O que faz:** É o **coração** do microserviço. Gerencia pessoas candidatas, classificação no concurso, convocação, eliminação, reclassificação e lotes.

**Para que serve:**

- Importar e consultar habilitados
- Calcular cotas e montar a fila de convocação
- Convocar, desconvocar, eliminar e reclassificar
- Apoiar reposição, reconvocação, extração de dados e SIGPEC
- Integrar com os módulos de Escolhas e Agenda

**Principais partes internas:**

.. list-table:: Módulos do app candidatos
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models/``
     - Candidato, lote, habilitado no concurso, eliminação e reclassificação
   * - ``api/views/``
     - Endpoints REST (candidatos, habilitados, eliminados, reclassificados)
   * - ``service/``
     - Regras de negócio e chamadas a outros microserviços
   * - ``repository/``
     - Acesso ao banco de dados (consultas e persistência)
   * - ``serializer/``
     - Validação e conversão dos dados da API
   * - ``management/commands/``
     - Comandos de apoio em desenvolvimento
   * - ``tests/``
     - Testes automatizados do app

**Exemplo:** Quando o analista pede “50 habilitados calculados” para um cargo, é o app ``candidatos`` que aplica as cotas, consulta o Módulo Escolhas e devolve a lista ordenada.

``apps/parametrizacao/``
~~~~~~~~~~~~~~~~~~~~~~~~

**O que faz:** Guarda os **percentuais padrão** de cotas PCD e NNA usados no cálculo de habilitados.

**Para que serve:**

- Consultar os percentuais vigentes
- Atualizar PCD e NNA quando a regra padrão do sistema mudar

**Analogia:** É o “ajuste fino” da calculadora de cotas — em vez de fixar 5% e 20% no código, esses valores ficam cadastrados e podem ser alterados pela equipe.

Pasta ``config/``
-----------------

**O que faz:** Configurações centrais do projeto Django.

**Para que serve:**

.. list-table:: Arquivos de configuração
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Função
   * - ``settings.py``
     - Banco de dados, apps instalados, CORS, URLs dos outros microserviços, idioma e fuso horário
   * - ``urls.py``
     - Rotas da API (``/api/v1/``), admin, healthcheck e Swagger
   * - ``wsgi.py``
     - Ponto de entrada para servidores de produção

**Exemplo:** As variáveis ``ESCOLHAS_API_URL`` e ``AGENDAS_API_URL`` em ``settings.py`` dizem ao sistema onde buscar escolhas e onde remover agendas.

Pasta ``requirements/``
-----------------------

**O que faz:** Lista as **dependências Python** do projeto, separadas por ambiente.

**Para que serve:**

.. list-table:: Arquivos de dependências
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Conteúdo
   * - ``base.txt``
     - Dependências essenciais (Django, DRF, PostgreSQL)
   * - ``local.txt``
     - Desenvolvimento (testes, lint, Sphinx)
   * - ``production.txt``
     - Produção (servidor de aplicação e itens de ambiente)

Pasta ``docs/``
---------------

**O que faz:** Contém esta documentação em formato reStructuredText (``.rst``) e a configuração do Sphinx.

**Para que serve:** Gerar o site HTML de documentação com ``make docs`` ou ``sphinx-build``.

Arquivos na raiz
----------------

.. list-table:: Arquivos na raiz do projeto
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Função
   * - ``manage.py``
     - Comando Django (migrações, servidor, superusuário)
   * - ``docker-compose.yml``
     - Sobe API e banco juntos no ambiente local
   * - ``Dockerfile``
     - Constrói a imagem Docker da API
   * - ``Makefile``
     - Atalhos: testes, lint, migrações e documentação
   * - ``README.md``
     - Visão técnica rápida e instruções de execução
   * - ``env.example``
     - Modelo de variáveis de ambiente necessárias

API — endpoints principais (referência)
---------------------------------------

Para consulta rápida, os principais caminhos da API (prefixo ``/api/v1/``):

**Candidatos**

- ``GET /candidatos/`` — Listar candidatos
- ``POST /candidatos/`` — Importar habilitados em lote
- ``GET /candidatos/buscar/`` — Buscar por nome, CPF, RG ou registro funcional

**Habilitados**

- ``GET /habilitados/`` — Listar habilitados (último lote do concurso)
- ``GET /habilitados/calculados/`` — Montar a fila de convocação com cotas
- ``PATCH /habilitados/convocar/`` — Marcar como convocados
- ``PATCH /habilitados/desconvocar/`` — Remover convocação
- ``POST /habilitados/eliminar/`` — Eliminar candidato
- ``POST /habilitados/reclassificar/`` — Reclassificar (ou reverter por mandado)
- ``GET /habilitados/reposicao/`` — Candidatos para reposição
- ``GET /habilitados/reconvocacao/`` — Candidatos para reconvocação
- ``POST /habilitados/extracao-dados/`` — Indicadores de habilitados e convocados
- ``POST /habilitados/salvar-lotes/`` — Importar lotes SIGPEC
- ``GET /habilitados/numeros-lote/`` — Números de lote distintos
- ``GET /habilitados/cargos/`` — Cargos para exportação SIGPEC

**Eliminados e reclassificados**

- ``GET /eliminados/`` — Listar eliminados do processo
- ``GET /reclassificados/`` — Listar reclassificados do processo

**Parametrização**

- ``GET /parametrizacao/`` — Consultar percentuais de cotas
- ``PATCH /parametrizacao/{uuid}/`` — Atualizar percentuais

A documentação interativa da API (Swagger) está disponível em ``/api/docs/`` quando o servidor está rodando.

Resumo do que foi usado para desenvolver
----------------------------------------

Sem entrar em detalhes de código, o módulo foi construído com:

- **Django e Django REST Framework** — base da API e da organização do projeto
- **PostgreSQL** — armazenamento dos candidatos, lotes e históricos
- **Camada de serviços e repositórios** — regras de negócio separadas das consultas ao banco
- **Integrações HTTP** com os módulos de Escolhas e Agenda
- **Documentação da API (Swagger)** para consulta dos endpoints
- **Testes automatizados** para validar o comportamento das regras principais
- **Docker e Makefile** para padronizar execução local e rotinas do time
