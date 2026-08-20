from django.urls import path
from validacao.views.uploads.upload import SpedXmlView
from validacao.views.uploads.upload import DueView

urlpatterns = [
    path('sped_xml/', SpedXmlView.as_view(), name='sped_xml'),
    path('due/', DueView.as_view(), name='due'),
]