# Opção 1 - tudo pré definido 

✔ Tudo controlado
❌ Nada flexível
❌ Toda nova regra = deploy 

# Opção 2 - usuário digitar livremente 

✔ Flexível
❌ Alto risco de erro
❌ Sistema pode quebrar ou não reconhecer

OBS: pois entra onde eu disse na terça, condicionais precisam saber o que esperar

# Opção 3 - Recomendado 

✔ Sistema tem regras padrões
✔ Usuário pode criar novas regras 
✔ Ele salva no banco
✔ Automaticamente aparece no select 
✔ E ele seleciona

regras = Regra.objects.filter(tipo__nome='prefixo')

for regra in regras:
    if codigo.startswith(regra.valor):
        codigo = codigo[len(regra.valor):]
