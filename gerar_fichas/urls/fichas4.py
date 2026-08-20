from django.urls import path
from gerar_fichas.views.fichas4 import Fichas4

urlpatterns = [
    path('ficha4A/', Fichas4.ficha4A, name='ficha4A'),
    path('ficha4B/', Fichas4.ficha4B, name='ficha4B'),
    path('ficha4C/', Fichas4.ficha4C, name='ficha4C'),
]