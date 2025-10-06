from django.contrib import admin
from .models import Candidato, ConcursoCandidato, ConcursoCandidatosLote

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    """Admin configuration for Candidato model"""
    list_display = ['nome', 'cpf', 'email', 'status', 'cidade', 'estado', 'criado_em']
    list_filter = ['status', 'genero', 'cidade', 'estado', 'criado_em', 'esta_ativo']
    search_fields = ['nome', 'cpf', 'email', 'cidade', 'telefone']
    readonly_fields = ['criado_em', 'atualizado_em', 'esta_ativo']
    date_hierarchy = 'criado_em'
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
            'fields': ('criado_em', 'atualizado_em', 'esta_ativo'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ConcursoCandidato)
class ConcursoCandidatoAdmin(admin.ModelAdmin):
    list_display = ['candidato', 'candidato__nome', 'classificacao', 'classificacao_pcd', 'classificacao_nna', 'lote__concurso_uuid', 'criado_em']
    list_filter = ['lote__concurso_uuid', 'criado_em']
    search_fields = ['candidato__nome', 'lote', 'candidato__cpf', 'candidato__email', 'candidato__telefone', 'candidato__celular']
    readonly_fields = ['criado_em', 'atualizado_em', 'esta_ativo']
    date_hierarchy = 'criado_em'
    list_per_page = 25

@admin.register(ConcursoCandidatosLote)
class ConcursoCandidatosLoteAdmin(admin.ModelAdmin):
    list_display = ['concurso_nome', 'concurso_uuid', 'criado_em']
    list_filter = ['criado_em']
    search_fields = ['concurso_nome']
    readonly_fields = ['criado_em', 'atualizado_em', 'esta_ativo']
    date_hierarchy = 'criado_em'
    list_per_page = 25