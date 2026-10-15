"""Django settings for candidatos project."""

import os
import sys
import threading
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DJANGO_ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "local")
MS_PATH = os.environ.get("MS_PATH", "/ms-candidatos")
AMBIENTE_APLICACAO = os.environ.get("AMBIENTE_APLICACAO", DJANGO_ENVIRONMENT)

BASE_DIR = Path(__file__).resolve().parent.parent
# Adiciona a pasta 'apps' ao sys.path do Python
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-your-secret-key-here"
)
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "qa-api-sigla.sme.prefeitura.sp.gov.br",
    "hom-api-sigla.sme.prefeitura.sp.gov.br",
]
CSRF_TRUSTED_ORIGINS = [
    "https://qa-api-sigla.sme.prefeitura.sp.gov.br",
    "https://hom-api-sigla.sme.prefeitura.sp.gov.br",
]

# Application definition
INSTALLED_APPS = [
    "elasticapm.contrib.django",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "auditlog",
    "drf_spectacular",
    "core",
    "candidatos",
    "parametrizacao",
]

MIDDLEWARE = [
    "elasticapm.contrib.django.middleware.TracingMiddleware",
    "candidatos.middleware.CorrelationIdMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sigla_sdk.middlewares.AuditlogJWTMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DB_ENGINE = os.environ.get("DB_ENGINE", "django.db.backends.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.environ.get("DB_NAME", BASE_DIR / "db_sigla.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.environ.get("DB_NAME", "db_sigla"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

_ms_path_segment = (MS_PATH or "/ms-candidatos").strip("/")
if DJANGO_ENVIRONMENT != "local":
    STATIC_URL = f"/{_ms_path_segment}/django_static/"
    MEDIA_URL = f"/{_ms_path_segment}/media/"
else:
    STATIC_URL = "/django_static/"
    MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "sigla_sdk.autenticacao.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # 'rest_framework.permissions.IsAuthenticated',
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "core.openapi.EsquemaAutomatico",
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = (
    os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if os.environ.get("CORS_ALLOWED_ORIGINS")
    else []
)

CORS_ALLOWED_ORIGINS = [
    "https://qa-sigla.sme.prefeitura.sp.gov.br",
    "https://hom-sigla.sme.prefeitura.sp.gov.br",
]

# Audit Log settings
AUDITLOG_INCLUDE_ALL_MODELS = True

_thread_locals = threading.local()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "sigla_sdk.logging.json_formatter.CustomJsonFormatter",
            "format": (  # noqa: E501
                "%(levelname)s %(asctime)s %(module)s %(filename)s "
                "%(lineno)d %(funcName)s %(message)s"
            ),
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "elasticapm": {
            "level": "DEBUG",
            "class": "elasticapm.contrib.django.handlers.LoggingHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "elasticapm"],
            "level": "INFO",
            "propagate": False,
        },
        "candidatos": {
            "handlers": ["console", "elasticapm"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "elasticapm"],
            "level": "ERROR",
            "propagate": False,
        },
        "elasticapm.errors": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "elasticapm.logging": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

ELASTIC_APM = {
    "SERVICE_NAME": os.environ.get(
        "ELASTIC_APM_SERVICE_NAME", "SME-SIGLA-MS-Candidatos"
    ),
    "SECRET_TOKEN": os.environ.get("ELASTIC_APM_SECRET_TOKEN", ""),
    "SERVER_URL": os.environ.get(
        "ELASTIC_APM_SERVER_URL", "http://localhost:8200"
    ),
    "SERVER_TIMEOUT": os.environ.get("ELASTIC_APM_SERVER_TIMEOUT", "35s"),
    "ENVIRONMENT": os.environ.get(
        "ELASTIC_APM_ENVIRONMENT", AMBIENTE_APLICACAO
    ),
    "ENABLED": os.environ.get("ELASTIC_APM_ENABLED", "0") == "1",
    "CAPTURE_BODY": os.environ.get("ELASTIC_APM_CAPTURE_BODY", "all"),
    "CAPTURE_HEADERS": os.environ.get("ELASTIC_APM_CAPTURE_HEADERS", "1")
    == "1",
    "TRANSACTION_SAMPLE_RATE": float(
        os.environ.get("ELASTIC_APM_TRANSACTION_SAMPLE_RATE", "0.3")
    ),
    "METRICS_INTERVAL": os.environ.get("ELASTIC_APM_METRICS_INTERVAL", "10s"),
    "FLUSH_INTERVAL": os.environ.get("ELASTIC_APM_FLUSH_INTERVAL", "10s"),
    "MAX_BATCH_EVENT_COUNT": int(
        os.environ.get("ELASTIC_APM_MAX_BATCH_EVENT_COUNT", "1000")
    ),
    "MAX_QUEUE_EVENT_COUNT": int(
        os.environ.get("ELASTIC_APM_MAX_QUEUE_EVENT_COUNT", "1000")
    ),
    "TRANSACTION_MAX_SPANS": int(
        os.environ.get("ELASTIC_APM_TRANSACTION_MAX_SPANS", "500")
    ),
    "DJANGO_TRANSACTION_NAME_FROM_ROUTE": True,
    "LOG_LEVEL": os.environ.get("ELASTIC_APM_LOG_LEVEL", "INFO"),
    "LOG_ECS_REFORMATTING": os.environ.get(
        "ELASTIC_APM_LOG_ECS_REFORMATTING", "off"
    ),
    "RECORDING": True,
    "TRANSACTIONS_ROOT_UNNAMED": True,
    "CAPTURE_ERRORS": True,
    "CAPTURE_PERFORMANCE": True,
    "CAPTURE_TRANSACTIONS": True,
    "CAPTURE_SPANS": True,
    "CAPTURE_TRANSACTION_STACKTRACES": True,
    "CAPTURE_TRANSACTION_STACKTRACES_LIMIT": 10,
}

DESCRICAO_API = """
API do microsserviço de **candidatos** do SIGLA (SME-SP). Mantém o cadastro
dos candidatos e os seus **habilitados**: a inscrição de cada candidato em
um concurso, com as classificações, a situação de convocação, as
reclassificações, as eliminações e os dados de lote do SIGPEC.

## Conceitos

- **Candidato**: a pessoa, identificada pelo CPF.
- **Habilitado**: a inscrição de um candidato em um cargo de um concurso.
  O mesmo candidato tem um habilitado para cada concurso e cargo.
- **Categorias**: `GERAL` (ampla concorrência), `NNA` (negros, negras ou
  afrodescendentes) e `PCD` (pessoas com deficiência). Cada habilitado tem
  uma classificação por lista em que concorre e uma **categoria efetiva**,
  que é a lista pela qual ele é convocado.

## Autenticação

Envie o token **JWT** emitido pelo microsserviço de usuários no header
`Authorization: Bearer <token>`. Também são aceitos HTTP Basic e a sessão
do Django Admin. As rotas atendem chamadas sem credencial, mas uma
credencial **inválida** é recusada com **403**: o serviço não responde 401.

## Erros

- **400** com `{"detail": "..."}`: regra de negócio violada ou parâmetro
  obrigatório ausente.
- **400** com `{"<campo>": ["..."]}`: dados enviados inválidos.
- **400** com `{"mensagem": "...", "detail": "..."}`: falha ao salvar
  lotes do SIGPEC.
- **403** com `{"detail": "...", "code": "..."}`: credencial recusada.
- **404** com `{"detail": "..."}`: registro não encontrado.
- **500**: erro inesperado, sem corpo JSON padronizado.
- **503** com `{"detail": "..."}`: o MS-Escolhas não respondeu à consulta
  de reconvocações.

## Paginação

Só a listagem de candidatos é paginada, com `page` e 20 itens por página.
A resposta traz `count`, `next`, `previous` e `results`. As demais
listagens retornam um array simples.

## Seleção de campos

As consultas de habilitados aceitam `fields`, com os nomes dos campos
desejados separados por vírgula. Os campos não pedidos são omitidos da
resposta, o que reduz bastante o volume em listagens grandes.

## Rotas legadas

As operações marcadas como obsoletas vêm do CRUD genérico e não são usadas
pelos demais serviços do SIGLA. Estão documentadas porque continuam
expostas, mas não devem ser adotadas por novos consumidores.
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "Candidatos Sigla API",
    "DESCRIPTION": DESCRICAO_API,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {
            "name": "Candidatos",
            "description": (
                "Cadastro de candidatos e carga em lote das listas de "
                "habilitados de um concurso."
            ),
        },
        {
            "name": "Habilitados",
            "description": (
                "Consulta dos habilitados por concurso, processo, cargo e "
                "classificação, e totais para relatórios."
            ),
        },
        {
            "name": "Convocação de habilitados",
            "description": (
                "Seleção dos habilitados a convocar e registro da "
                "convocação em um processo."
            ),
        },
        {
            "name": "Reclassificação e eliminação",
            "description": (
                "Mudança de lista e eliminação de habilitados, e consulta "
                "dos atingidos em cada processo."
            ),
        },
        {
            "name": "Lotes SIGPEC",
            "description": (
                "Dados de lote, empresa e vaga devolvidos pelo SIGPEC para "
                "os habilitados."
            ),
        },
        {
            "name": "Parametrização",
            "description": (
                "Percentuais de reserva de vagas usados no cálculo da "
                "convocação."
            ),
        },
    ],
    "ENUM_NAME_OVERRIDES": {
        "CategoriaEnum": (
            "candidatos.models.concurso_candidato.CATEGORIA_CHOICES"
        ),
        "CotaEnum": "candidatos.constants.COTA_CHOICES",
    },
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "jwtAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": (
                    "Token JWT emitido pelo microsserviço de usuários do "
                    "SIGLA, enviado em `Authorization: Bearer <token>`."
                ),
            },
            # "ApiKeyAuth": {
            #     "type": "apiKey",
            #     "in": "header",
            #     "name": "X-API-Key",
            # },
        }
    },
    # "SECURITY": [{"ApiKeyAuth": []}],
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}

JWT_SIGNING_KEY = os.environ.get(
    "JWT_SIGNING_KEY",
    os.environ.get("SECRET_KEY", "fallback-só-dev"),
)

SIMPLE_JWT = {
    "SIGNING_KEY": JWT_SIGNING_KEY,
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1440),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

API_KEY = os.environ.get("API_KEY", "api-key-candidatos")
API_KEY_HEADER = os.environ.get("API_KEY_HEADER", "X-API-Key")

ESCOLHAS_API_URL = os.environ.get("ESCOLHAS_API_URL", "http://localhost:8004")
ESCOLHAS_API_KEY = os.environ.get("ESCOLHAS_API_KEY", "api-key-escolhas")
AGENDAS_API_URL = os.environ.get("AGENDAS_API_URL", "http://localhost:8005")
AGENDAS_API_KEY = os.environ.get("AGENDA_API_KEY", "api-key-agenda")
