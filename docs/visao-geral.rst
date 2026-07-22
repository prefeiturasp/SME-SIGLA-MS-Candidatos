Visão geral
===========

O que é este módulo?
--------------------

O **Módulo Candidatos** é o sistema responsável por guardar e operar a **lista de candidatos habilitados** em concursos da SME (Secretaria Municipal de Educação de São Paulo).

Em termos simples: depois que o concurso é homologado, a classificação dos aprovados precisa estar disponível para a convocação. Este módulo concentra esses dados, aplica as **cotas** (ampla, PCD e NNA), marca quem foi **convocado**, **eliminado** ou **reclassificado**, e apoia operações como reposição, reconvocação e integração com lotes SIGPEC.

Para que serve?
---------------

O sistema permite que a equipe da SME:

- **Importe e mantenha** os candidatos habilitados de cada concurso
- **Calcule quem entra** na próxima convocação, respeitando as cotas
- **Convocar e desconvocar** candidatos vinculados a um processo
- **Eliminar** candidatos (com histórico) e **reclassificar** quem sai de cota
- Apoiar **reposição** de vagas e **reconvocação** de quem ainda não escolheu
- Consultar **indicadores** (habilitados × convocados)
- Atualizar dados de **lotes SIGPEC** (empresa, vaga, registro funcional)
- Ajustar os **percentuais padrão** de cotas PCD e NNA

Onde ele se encaixa no ecossistema SIGLA?
-----------------------------------------

Este módulo **não trabalha sozinho**. Ele se integra com outros sistemas:

.. list-table:: Integrações do ecossistema
   :header-rows: 1
   :widths: 25 75

   * - Sistema
     - Papel em relação aos candidatos
   * - **Módulo Processos de Convocação**
     - Orquestra o processo e solicita habilitados / marca convocados
   * - **Módulo Escolhas**
     - Informa quem já escolheu vaga ou pediu reconvocação
   * - **Módulo Agenda**
     - Ao desconvocar por cargo, remove agendas daquele processo e cargo
   * - **Frontend SIGLA**
     - Interface usada pela equipe para operar habilitados e cotas

O Módulo Candidatos é a **fonte oficial da classificação e da situação** de cada habilitado no concurso.

Exemplo prático do dia a dia
----------------------------

Imagine o seguinte cenário:

1. O **Concurso Público 2026** para Professor de Educação Básica foi homologado.
2. A lista de habilitados é **importada** neste módulo (em um “lote” do concurso).
3. A SME abre um processo de convocação e pede, por exemplo, **50 candidatos** para um cargo.
4. O sistema **calcula a sequência** intercalando ampla concorrência, PCD e NNA, considerando quem já escolheu no Módulo Escolhas.
5. Os candidatos selecionados são **marcados como convocados** e passam a aparecer no processo.
6. Se alguém for desclassificado de cota (NNA ou PCD), registra-se a **reclassificação**; se for desligado do processo, a **eliminação**.
7. Quando necessário, a equipe usa **reposição** ou **reconvocação** para completar vagas.

Fluxo resumido
--------------

.. code-block:: text

   Importação dos habilitados (lote do concurso)
            |
            v
   Parametrização de cotas (PCD / NNA)
            |
            v
   Cálculo de quem será convocado  <---  Módulo Escolhas
            |
            v
   Convocar / Desconvocar  --->  Módulo Agenda (na desconvocação)
            |
            +-- Eliminar / Reclassificar
            +-- Reposição / Reconvocação
            +-- Extração de dados / Lotes SIGPEC

Tecnologias utilizadas (referência rápida)
------------------------------------------

Para quem precisa de contexto técnico sem entrar no código:

- **Django** — framework web que estrutura o projeto
- **Django REST Framework** — expõe a API consumida pelo frontend e pelos outros módulos
- **PostgreSQL** — banco de dados onde ficam candidatos, classificações e históricos
- **Docker** — facilita subir o serviço em ambientes padronizados
- **Swagger (documentação da API)** — consulta interativa dos endpoints em ``/api/docs/``
