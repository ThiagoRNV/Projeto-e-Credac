from django.urls import path
from validacao.views.nfe.processar_spedxml import ProcessamentoFiscalView 
from validacao.views.nfe.processar_due import ProcessamentoDueView

urlpatterns = [
    path('processar_arquivos/', ProcessamentoFiscalView.as_view(), name='processar_arquivos'),
    path('processar_due', ProcessamentoDueView.as_view(), name='processar_planilha_due'),
]