from django.urls import path
from cadastro.views.regras.regras import Regras

urlpatterns = [
    path('', Regras.as_view(), name='tela_regras'),
    path('regras_cod_lan/', Regras.as_view(), name='regras_cod_lan'),
]
