from django.urls import path
from gerar_fichas.views.fichas3 import Fichas3

urlpatterns = [
    path('ficha3A/', Fichas3.ficha3A, name='ficha3A'),
    path('ficha3B/', Fichas3.ficha3B, name='ficha3B'),
    path('ficha3C/', Fichas3.ficha3C, name='ficha3C'),
]