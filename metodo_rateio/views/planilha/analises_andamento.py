from django.shortcuts import render, redirect
from django.views import View

class AnalisesEmAndamentoPlanilha(View):

    def get(request):
        return render(request, 'planilha/analises_andamento_planilha.html')