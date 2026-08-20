from django.urls import path
from cadastro.views.produto.cadastro_manualmente import CadastroItensManual
from cadastro.views.produto.editar_productViaSped import UpdateProductsViaSped as update_sped
from cadastro.views.produto.excluir_dados_viaSped import DeleteProductsViaSped as delete_sped

urlpatterns = [
    path('produto/cadastro_produtos/', CadastroItensManual.as_view(), name='cadastrar_manual'),
    path('produto_sped/editar/<int:id>/', update_sped.as_view(), name='editar_produto'),
    path('produto_sped/excluir/<int:id>/', delete_sped.as_view(), name='excluir_produto_sped'),
]
