from django.urls import path # type: ignore
from gerar_arquivo.views.gerar_arquivo import GerarArquivo 

urlpatterns = [
    path('gerar_arquivo/', GerarArquivo.as_view(), name='gerar_arquivo'),
]
    