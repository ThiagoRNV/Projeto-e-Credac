from django.urls import path
from metodo_rateio.views.sped.processamento import ProcessamentoView
from metodo_rateio.views.sped.dataframes import DataFrameViewK23x, DataFrameViewK25x
from metodo_rateio.views.sped.analises_andamento import AnalisesEmAndamentoK23x, AnalisesEmAndamentoK25x
from metodo_rateio.views.sped.processamento import TelaUploadView 

urlpatterns = [
    path('tela_para_processamento/', TelaUploadView.as_view(), name='tela_para_processamento_sped'),
    path('processamento/', ProcessamentoView.as_view(), name='processamento'),
    path('view_producao_k230_k235/', DataFrameViewK23x.as_view(), name='view_producao_k230_k235'),
    path('view_producao_k250_k255/', DataFrameViewK25x.as_view(), name='view_producao_k250_k255'),
    path('analiseproducao/', AnalisesEmAndamentoK23x.as_view(), name='analise_bloco_k23x'),
    path('analiseindustrializacao/', AnalisesEmAndamentoK25x.as_view(), name='analise_bloco_k25x'),
]