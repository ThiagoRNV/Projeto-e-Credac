from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from cadastro.models.empresa import Empresa
from validacao.views.nfe.processar_spedxml import ProcessamentoFiscalView 
from validacao.views.outros_modelos.processamento import ProcessamentoServicoView

class SpedXmlView(View):

    def get(self, request):
        empresas = Empresa.objects.all()
        context = {     
            'empresas': empresas,
            'nova_empresa': None 
        }
        return render(request, 'upload_arquivos/upload_sped_xml.html', context)

    def post(self, request):
        
        btn = request.POST.get('btn')
        
        print(btn)

        if btn is None:
            return redirect ('sped_xml')

        if btn == 'processar':
            ProcessamentoFiscalView.as_view()(request) 
            ProcessamentoServicoView.as_view()(request)

            return redirect ('sped_xml')


class DueView(View):

    def get(self, request):
        return render(request, 'upload_arquivos/upload_due.html')
