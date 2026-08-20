from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect
from validacao.services.nfe.process.processar_due import DueException, DueTypeError, ErrorDate, ProcessDueService

class ProcessamentoDueView(View):
    def post(request):
        if request.method != 'POST':
            messages.warning(request, 'Método não permitido. Use o formulário para processar o arquivo.')
            return redirect('upload_due')

        planilha_due = request.FILES.get('due_file')

        services = ProcessDueService(planilha_due)

        try:
            process_ok = services.due()

            completed = process_ok.get('success')

            if completed:
                messages.success(request, 'Arquivo processado com sucesso.')
                return redirect ('upload_due')
        except DueException as e:
            return HttpResponse(
                'Não foi possível realizar sua solicitação. Favor entrar em contato com o suporte.',
                status=500
            )

        except ErrorDate as e:
            messages.warning(request, str(e))
            return redirect ('upload_due')

        except DueTypeError as e:
            messages.error(request, str(e))