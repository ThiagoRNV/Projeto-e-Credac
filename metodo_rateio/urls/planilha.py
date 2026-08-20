from django.urls import path
from metodo_rateio.views.planilha.processamento import ProcessamentoXlsx
from metodo_rateio.views.planilha.view_planilha import ViewPlanilha
from metodo_rateio.views.planilha.analises_andamento import AnalisesEmAndamentoPlanilha
from metodo_rateio.views.planilha.processamento import TelaParaProcessamento
urlpatterns = [
    path('tela_para_processamento/', TelaParaProcessamento.as_view(), name='tela_para_processamento_planilha'),
    path('processamento_planilha/', ProcessamentoXlsx.as_view(), name='processamento_planilha'),
    path('view_analisePlanilha/', ViewPlanilha.as_view(), name='view_analisePlanilha'),
    path('analises_andamento_planilha/', AnalisesEmAndamentoPlanilha.as_view(), name='analises_andamento_planilha'),
]