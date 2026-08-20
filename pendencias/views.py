from django.shortcuts import render
from django.views import View

class TelaPendenciasView(View):

    def get(self, request):
        return render (request, 'pendencias.html')
