from django.urls import path
from cadastro.views.empresa.cadastro_manualmente import CadastrarManual
from cadastro.views.empresa.editar_job import Editarjob
from cadastro.views.empresa.excluir_job import ExcluirJob
from cadastro.views.empresa.cadastro_via_sped import CadastrarViaSped

urlpatterns = [
    path('nova/', CadastrarManual.as_view(), name='cadastrar_manualmente'),
    path('empresa/editar/<int:id>/', Editarjob.as_view(), name='editar_empresa'),
    path('empresa/excluir/<int:id>/', ExcluirJob.as_view(), name='excluir_empresa'),
    path('empresa/cadastrar_empresa/', CadastrarViaSped.as_view(), name='cadastrar_via_sped'),
]
