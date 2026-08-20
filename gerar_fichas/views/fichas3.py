from django.shortcuts import render

class Fichas3:

    def ficha3A(request):
        return render(request, 'fichas3/ficha3A.html')

    def ficha3B(request):
        return render(request, 'fichas3/ficha3B.html')
    
    def ficha3C(request):
        return render(request, 'fichas3/ficha3C.html')