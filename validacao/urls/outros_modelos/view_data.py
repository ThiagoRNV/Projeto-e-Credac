from django.urls import path
from validacao.views.outros_modelos.dataframe import DataFrameServicos

urlpatterns = [
    path("view-dados-servicos/", DataFrameServicos.as_view(), name="view_dados_outros_modelos"),
]
