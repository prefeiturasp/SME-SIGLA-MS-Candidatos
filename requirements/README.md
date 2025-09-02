# Requirements

Este diretório contém os arquivos de dependências do projeto organizados por ambiente.

## Arquivos

- **base.txt**: Dependências básicas necessárias para todos os ambientes
- **local.txt**: Dependências adicionais para desenvolvimento local
- **production.txt**: Dependências adicionais para produção

## Instalação

### Ambiente Local (Desenvolvimento)
```bash
pip install -r requirements/local.txt
```

### Produção
```bash
pip install -r requirements/production.txt
```

### Apenas Dependências Básicas
```bash
pip install -r requirements/base.txt
```

## Dependências Principais

- **Django 5.2.5**: Framework web principal
- **Django REST Framework 3.15.2**: Para APIs REST
- **Django CORS Headers 4.7.0**: Para permitir requisições cross-origin
- **Django Filter 25.1**: Para filtros avançados nas APIs
- **Django Audit Log 3.2.1**: Para auditoria de mudanças nos modelos
- **psycopg2-binary 2.9.9**: Driver PostgreSQL para Python
