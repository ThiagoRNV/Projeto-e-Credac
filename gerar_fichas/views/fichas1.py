from django.shortcuts import render

class Fichas1:

    def ficha1A(request):
        return render(request, 'fichas1/ficha1A.html')

    def ficha1B(request):
        return render(request, 'fichas1/ficha1B.html')

    def ficha1C(request):
        return render(request, 'fichas1/ficha1C.html')

    def ficha1D(request):
        return render(request, 'fichas1/ficha1D.html')

    def ficha1E(request):
        return render(request, 'fichas1/ficha1E.html')