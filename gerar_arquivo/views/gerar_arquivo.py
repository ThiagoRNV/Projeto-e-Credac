from collections.abc import ItemsView
from operator import truediv
from django.shortcuts import render
from cadastro.models.empresa import Empresa
from django.contrib import messages
from django.shortcuts import redirect, render
import logging
from cadastro.models.empresa import Empresa
from django.views import View
from gerar_arquivo.services.gerar_arquivo import ArquivoServices


logger = logging.getLogger(__name__)


class GerarArquivo(View):

    def get(self, request):

        empresas = Empresa.objects.all().filter(status=True)

        return render(
            request,
            "gerar_arquivo.html",
            {
                "empresas": empresas,
            },
        )
    def post(self, request):

        service = ArquivoServices(request.POST)
    
        return service.gerar_arquivo()
        