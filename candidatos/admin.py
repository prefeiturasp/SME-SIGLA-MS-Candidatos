from django.contrib import admin
from .models import Candidato

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    """Admin configuration for Candidato model"""
    list_display = ['nome', 'cpf', 'email', 'status', 'cidade', 'estado', 'created_at']
    list_filter = ['status', 'genero', 'cidade', 'estado', 'created_at', 'is_active']
    search_fields = ['nome', 'cpf', 'email', 'cidade', 'telefone']
    readonly_fields = ['created_at', 'updated_at', 'is_active']
    date_hierarchy = 'created_at'
    list_per_page = 25
    list_editable = ['status']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'email', 'telefone', 'data_nascimento', 'genero')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Status e Observações', {
            'fields': ('status', 'observacoes')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'is_active'),
            'classes': ('collapse',)
        }),
    )
