from django.urls import path
from validacao.views.nfe.mercadorias_em_andamento import MercadoriasView as mv

# URLs - nfe (NF-e)
urlpatterns = [
    path('painel_de_controle/', mv.mercadorias_em_andamento, name='mercadorias_em_andamento'),
    path('finalizar_movimentacao/', mv.finalizar_movimentacao, name='finalizar_movimentacao'),
    path('mover_para_edicao/', mv.mover_para_edicao, name='mover_para_edicao'),
] 