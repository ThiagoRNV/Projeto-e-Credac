from django.urls import path
from gerar_fichas.views.fichas5 import Fichas5

urlpatterns = [
    path('ficha5A/', Fichas5.ficha5A, name='ficha5A'),
    path('ficha5B/', Fichas5.ficha5B, name='ficha5B'),
    path('ficha5C/', Fichas5.ficha5C, name='ficha5C'),
    path('ficha5D/', Fichas5.ficha5D, name='ficha5D'),
    path('ficha5F/', Fichas5.ficha5F, name='ficha5F'),
    path('ficha5G/', Fichas5.ficha5G, name='ficha5G'),
    path('ficha5H/', Fichas5.ficha5H, name='ficha5H'),
    path('ficha5I/', Fichas5.ficha5I, name='ficha5I'),
]