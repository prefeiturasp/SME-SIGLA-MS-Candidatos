from django.contrib import admin, messages
from .models import Candidato, ConcursoCandidato, ConcursoCandidatosLote

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    """Admin configuration for Candidato model"""
    list_display = ['nome', 'cpf', 'email', 'status', 'cidade', 'estado', 'criado_em']
    list_filter = ['status', 'genero', 'cidade', 'estado', 'criado_em', 'esta_ativo']
    search_fields = ['nome', 'cpf', 'email', 'cidade', 'telefone']
    readonly_fields = ['criado_em', 'atualizado_em', 'esta_ativo']
    date_hierarchy = 'criado_em'
    list_per_page = 26
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
    list_display = ['candidato', 'candidato__nome', 'codigo_cargo', 'processo_uuid', 'classificacao', 'classificacao_pcd', 'classificacao_nna', 'foi_convocado', 'data_convocacao', 'lote__concurso_uuid', 'criado_em']
    list_filter = ['lote__concurso_uuid', 'criado_em', 'foi_convocado', 'data_convocacao', 'processo_uuid', 'codigo_cargo']
    search_fields = ['candidato__nome', 'lote', 'candidato__cpf', 'candidato__email', 'candidato__telefone', 'candidato__celular']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em', 'esta_ativo']
    date_hierarchy = 'criado_em'
    list_per_page = 25
    actions = ['marcar_nao_convocados']

    def marcar_nao_convocados(self, request, queryset):
        """
        Ação de admin para marcar registros como não convocados em lote.
        """
        qtd = queryset.update(foi_convocado=False, data_convocacao=None)
        self.message_user(
            request,
            f'{qtd} registro(s) marcados como não convocados.',
            level=messages.SUCCESS
        )
    marcar_nao_convocados.short_description = 'Marcar como NÃO convocados (foi_convocado=False)'

@admin.register(ConcursoCandidatosLote)
class ConcursoCandidatosLoteAdmin(admin.ModelAdmin):
    list_display = ['concurso_nome', 'concurso_uuid', 'criado_em']
    list_filter = ['criado_em']
    search_fields = ['concurso_nome']
    readonly_fields = ['criado_em', 'atualizado_em', 'esta_ativo']
    date_hierarchy = 'criado_em'
    list_per_page = 25