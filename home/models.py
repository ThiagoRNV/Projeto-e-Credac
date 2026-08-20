from django.db import models
from django.contrib.auth.models import User

class Permissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    gerar_arquivo = models.BooleanField('Tela Gerar arquivo', default=True)
    cadastro = models.BooleanField('Tela Cadastro', default=True)
    metodo_rateio = models.BooleanField('Tela Método Rateio', default=True)
    movimentacao = models.BooleanField('Tela Movimentações', default=True)
    gerar_fichas = models.BooleanField('Tela Gerar Fichas', default=True)

    