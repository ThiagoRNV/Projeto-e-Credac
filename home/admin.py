from django.contrib import admin
from .models import Permissions

@admin.register(Permissions)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('user', 'gerar_arquivo', 'cadastro',
                    'metodo_rateio', 'movimentacao', 'gerar_fichas' )

    search_fields = ('user', 'gerar_arquivo', 'cadastro',
                'metodo_rateio', 'movimentacao', 'gerar_fichas' )