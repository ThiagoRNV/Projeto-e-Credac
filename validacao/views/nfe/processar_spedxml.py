from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from validacao.services.nfe.process.processar_spedxml import EmptyListNfe, NotCompainer, ProcessSpedXml, SpedXmlException, SpedXmlTypeError


import logging
logger = logging.getLogger(__name__)

class ProcessamentoFiscalView(View):

    def post(self, request):

        try:
            sped_file = request.FILES.get('sped_files')
            folder_xml = request.FILES.getlist('folder_input')
            
            services = ProcessSpedXml(sped_file, folder_xml)
            
            processamento = services.process()

            razao_social = processamento.get('razao_social')
            empresa_id = processamento.get('empresa_id')
            success = processamento.get('success')
            
            request.session['empresa_id'] = empresa_id

            if success:
                messages.success(request, f'Arquivos processados com sucesso da empresa {razao_social}')
                return redirect ('sped_xml')

        except SpedXmlException as e:
            return HttpResponse(
                'Não possível realizar sua solicitação. Favor entrar em contato com o suporte.',
                status=500
            )

        except SpedXmlTypeError as e:
            messages.error(request, str(e))
            return redirect ('sped_xml')

        except EmptyListNfe as e:
            messages.error(request, str(e))
            return redirect ('sped_xml')
            
        except NotCompainer as e:
            messages.warning(request, str(e))
            return redirect ('sped_Xml')

  