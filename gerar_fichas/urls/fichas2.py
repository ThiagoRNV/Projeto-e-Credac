from django.urls import path
from gerar_fichas.views.fichas2 import Fichas2

urlpatterns = [
    path('ficha2A/', Fichas2.ficha2A, name='ficha2A'),
    path('ficha2B/', Fichas2.ficha2B, name='ficha2B'),
    path('ficha2C/', Fichas2.ficha2C, name='ficha2C'),
    path('ficha2D/', Fichas2.ficha2D, name='ficha2D'),
    path('ficha2E/', Fichas2.ficha2E, name='ficha2E'),
    path('ficha2F/', Fichas2.ficha2F, name='ficha2F'),
    path('ficha2G/', Fichas2.ficha2G, name='ficha2G'),
]