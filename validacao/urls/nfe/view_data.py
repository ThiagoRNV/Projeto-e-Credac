from django.urls import path # type: ignore
from validacao.views.nfe.dataframe import DataFrame

urlpatterns = [
    path("movimentacoes/", DataFrame.as_view(), name="view_dados_nfe"),
]