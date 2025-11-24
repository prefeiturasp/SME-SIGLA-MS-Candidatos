# SME-SIGLA-MS-Candidatos

Microserviço para gerenciamento de candidatos do sistema SME-SIGLA.

## Descrição

Este microserviço é responsável por gerenciar:
- Cadastro completo de candidatos
- Documentos dos candidatos
- Experiências profissionais
- Informações pessoais e de contato

## Funcionalidades

- **Candidatos**: CRUD completo para candidatos
- **Documentos**: Gerenciamento de documentos pessoais e profissionais
- **Experiências**: Histórico profissional dos candidatos
- **APIs REST**: Endpoints para integração com outros sistemas
- **Admin Django**: Interface administrativa para gestão
- **Auditoria**: Log de todas as alterações nos modelos

## Tecnologias

- Django 5.2.5
- Django REST Framework 3.15.2
- PostgreSQL
- Docker
- Django CORS Headers
- Django Filter
- Django Audit Log

## Estrutura do Projeto

```
SME-SIGLA-MS-Candidatos/
├── config/                 # Configurações do Django
├── candidatos/            # Aplicação principal
│   ├── models/            # Modelos de dados
│   ├── views.py           # ViewSets da API
│   ├── serializers.py     # Serializers da API
│   ├── admin.py           # Configuração do Admin
│   ├── urls.py            # URLs da aplicação
│   └── utils.py           # Utilitários
├── requirements/           # Dependências Python
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
└── manage.py              # Script de gerenciamento Django
```

## Instalação e Configuração

### Pré-requisitos

- Python 3.12+
- PostgreSQL
- Docker (opcional)

### Ambiente Local

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd SME-SIGLA-MS-Candidatos
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements/local.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. **Execute as migrações**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crie um superusuário**
   ```bash
   python manage.py createsuperuser
   ```

7. **Execute o servidor**
   ```bash
   python manage.py runserver
   ```

### Com Docker

1. **Configure as variáveis de ambiente**
   ```bash
   cp env.example .env
   ```

2. **Execute com Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Uso

### URLs Principais

- **Admin**: http://localhost:8001/admin/
- **API**: http://localhost:8001/api/
- **Candidatos**: http://localhost:8001/api/candidatos/
- **Documentos**: http://localhost:8001/api/documentos/
- **Experiências**: http://localhost:8001/api/experiencias/

### Comandos Úteis

- **Executar testes**:
  ```bash
  python manage.py test
  ```

- **Coletar arquivos estáticos**:
  ```bash
  python manage.py collectstatic
  ```

## API Endpoints

### Candidatos

- `GET /api/candidatos/` - Lista todos os candidatos
- `POST /api/candidatos/` - Cria um novo candidato
- `GET /api/candidatos/{id}/` - Obtém detalhes de um candidato
- `PUT /api/candidatos/{id}/` - Atualiza um candidato
- `DELETE /api/candidatos/{id}/` - Remove um candidato

### Documentos

- `GET /api/documentos/` - Lista todos os documentos
- `POST /api/documentos/` - Cria um novo documento
- `GET /api/documentos/{id}/` - Obtém detalhes de um documento
- `PUT /api/documentos/{id}/` - Atualiza um documento
- `DELETE /api/documentos/{id}/` - Remove um documento

### Experiências

- `GET /api/experiencias/` - Lista todas as experiências
- `POST /api/experiencias/` - Cria uma nova experiência
- `GET /api/experiencias/{id}/` - Obtém detalhes de uma experiência
- `PUT /api/experiencias/{id}/` - Atualiza uma experiência
- `DELETE /api/experiencias/{id}/` - Remove uma experiência

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.