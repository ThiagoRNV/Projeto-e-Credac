from django.contrib import admin
from historico.models import Historico


@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('data_alteracao', 'tela_modificada', 'campo', 'usuario', 'mes_sped', 'ano_sped')
    list_filter = ('tela_modificada',)
