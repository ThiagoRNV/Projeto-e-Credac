from django.urls import path
from gerar_fichas.views.menu_fichas import MenuFichas

urlpatterns = [
    path('menu_fichas/', MenuFichas.menu_fichas, name='menu_fichas'),
]