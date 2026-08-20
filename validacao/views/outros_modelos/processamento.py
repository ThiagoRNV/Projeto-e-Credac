from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from validacao.services.outros_modelos.process_outros_modelos.processamento import CompaineError, EmptyList, ProcessServices, SpedException, SpedFormatError

from django.http import HttpResponse, HttpResponseServerError

class ProcessamentoServicoView(View):
    
    def post(self, request):

        sped_file = request.FILES.get('sped_files')
        
        services = ProcessServices(sped_file) 
        process = services.processamento_service()

        try:
            success = process.get('success')
            empresa_obj = process.get('empresa_obj')

            if success:
                messages.success(request, f'Arquivo processado com sucesso para a empresa {empresa_obj.razao_social}')
                return redirect ('sped_xml')

            request.session['empresa_id'] = empresa_obj.id

        except EmptyList as e:
            messages.error(request, str(e))
            return redirect ('sped_xml')

        except SpedFormatError as e:
            messages.error(request, str(e))
            return redirect ('sped_xml')

        except SpedException:
            return HttpResponseServerError(
                'Erro ao realizar o processo, Favor entrar em contato com o suporte',
                status=500
            )

        except CompaineError as e:
            messages.error(request, str(e))
            return redirect ('sped_xml')

        
