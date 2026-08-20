from django.urls import path
from gerar_fichas.views.fichas1 import Fichas1

urlpatterns = [
    path('ficha1A/', Fichas1.ficha1A, name='ficha1A'),
    path('ficha1B/', Fichas1.ficha1B, name='ficha1B'),
    path('ficha1C/', Fichas1.ficha1C, name='ficha1C'),
    path('ficha1D/', Fichas1.ficha1D, name='ficha1D'),
    path('ficha1E/', Fichas1.ficha1E, name='ficha1E'),
]