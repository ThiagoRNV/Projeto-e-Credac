from django.contrib import admin
from cadastro.models.empresa import Empresa, Regra, EmpresaRegra

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'inscricao_estadual', 'uf', 
                    'indicador_atividade', 'configuracao', 
                    'codigo_municipio', 'status' )

    search_fields = ('razao_social', 'cnpj', 'inscricao_estadual', 'uf', 
                    'indicador_atividade', 'configuracao', 
                    'codigo_municipio', 'status' )

@admin.register(Regra)
class RegrasAdmin(admin.ModelAdmin):
    list_display = ('regra', 'tipo')
    list_filter = ('regra', 'tipo')
    search_fields = ('regra', 'tipo')
    
    class Media:
        js = ('js/regras_admin.js',)

@admin.register(EmpresaRegra)
class EmpresaRegraAdmin(admin.ModelAdmin):
    list_display = ('empresa_id', 'regra_id', 'status')
    list_filter = ('empresa_id', 'regra_id', 'status')
    search_fields = ('empresa_id', 'regra_id', 'status')
   