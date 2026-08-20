from django.urls import path
from pendencias.views import TelaPendenciasView

urlpatterns = [
    path('pendencias/', TelaPendenciasView.as_view(), name='pendencias' )
]
