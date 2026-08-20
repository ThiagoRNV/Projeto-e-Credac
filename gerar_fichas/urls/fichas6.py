from django.urls import path
from gerar_fichas.views.fichas6 import Fichas6

urlpatterns = [
    path('ficha6A/', Fichas6.ficha6A, name='ficha6A'),
    path('ficha6B/', Fichas6.ficha6B, name='ficha6B'),
    path('ficha6C/', Fichas6.ficha6C, name='ficha6C'),
    path('ficha6D/', Fichas6.ficha6D, name='ficha6D'),
    path('ficha6E/', Fichas6.ficha6E, name='ficha6E'),
    path('ficha6F/', Fichas6.ficha6F, name='ficha6F'),
    path('ficha6G/', Fichas6.ficha6G, name='ficha6G'),
    path('ficha6H/', Fichas6.ficha6H, name='ficha6H'),
]