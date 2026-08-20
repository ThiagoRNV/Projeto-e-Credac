from django.shortcuts import render

class Fichas4:

    def ficha4A(request):
        return render(request, 'fichas4/ficha4A.html')

    def ficha4B(request):
        return render(request, 'fichas4/ficha4B.html')

    def ficha4C(request):
        return render(request, 'fichas4/ficha4C.html')