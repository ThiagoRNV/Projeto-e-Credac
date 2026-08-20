from .models import Permissions

def permissoes(request):
    if request.user.is_authenticated:
        permissions = Permissions.objects.filter(user=request.user)

        return {
            'gerar_arquivo': any(p.gerar_arquivo for p in permissions),
            'cadastro': any(p.cadastro for p in permissions),
            'metodo_rateio': any(p.metodo_rateio for p in permissions),
            'movimentacao': any(p.movimentacao for p in permissions),
            'gerar_fichas': any(p.gerar_fichas for p in permissions),
        }

    return {
        'gerar_arquivo': False,
        'cadastro': False,
        'metodo_rateio': False,
        'movimentacao': False,
        'gerar_fichas': False,
    }