"""Admin do app parametrizacao."""

from django.contrib import admin

from .models import Parametrizacao


@admin.register(Parametrizacao)
class ParametrizacaoAdmin(admin.ModelAdmin):
    """Admin configuration for Parametrizacao model."""

    list_display = [
        "uuid",
        "porcentagem_pcd",
        "porcentagem_nna",
        "criado_em",
        "atualizado_em",
    ]
    list_filter = ["criado_em", "atualizado_em", "esta_ativo"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em", "esta_ativo"]
    date_hierarchy = "criado_em"
    list_per_page = 25
    fieldsets = (
        (
            "Parâmetros de Cálculo",
            {"fields": ("porcentagem_pcd", "porcentagem_nna")},
        ),
        (
            "Metadados",
            {
                "fields": ("uuid", "criado_em", "atualizado_em", "esta_ativo"),
                "classes": ("collapse",),
            },
        ),
    )
