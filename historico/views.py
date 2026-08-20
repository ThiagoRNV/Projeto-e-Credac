from collections import OrderedDict

from django.shortcuts import render
from historico.models import Historico


TELA_LABELS = OrderedDict(Historico.TELA_CHOICES)


def historico(request):
    historicos = list(Historico.objects.select_related('usuario').all())

    historicos_por_tela = OrderedDict()
    for chave, label in TELA_LABELS.items():
        itens = [h for h in historicos if h.tela_modificada == chave]
        if itens:
            historicos_por_tela[chave] = {
                'label': label,
                'itens': itens,
            }

    return render(request, 'historico.html', {
        'historicos_por_tela': historicos_por_tela,
        'total_historicos': len(historicos),
    })
