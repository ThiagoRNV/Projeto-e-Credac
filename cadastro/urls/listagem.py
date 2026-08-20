from django.urls import path
from cadastro.views.empresa.listagem_empresas import EmpresaView
from cadastro.views.produto.listagem_via_sped import ListarProdutosSped as listagem

urlpatterns = [
    path('lista_empresas/', EmpresaView.as_view(), name='lista_empresas'),
    path('listagem_sped/', listagem.as_view(), name='lista_produtos_sped'),
]
