from django.shortcuts import render

class MenuFichas:

    def menu_fichas(request):
        return render(request, 'menu/menu_fichas.html')


