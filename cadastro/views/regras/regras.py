from django.shortcuts import render
from cadastro.models.empresa import Empresa
from validacao.models.mercadorias_nfe.notas import Notas_participantes
from validacao.models.participantes.participantes import Participantes
from validacao.models.mercadorias_nfe.produtos import Produtos_notas
from django.contrib import messages
from django.views import View

class Regras(View):

    def get(self, request):

        empresas = Empresa.objects.all().filter(status=True)

        return render(request, 'regras/regras.html',
            {
                'empresas': empresas
            }
        )

    def post(self, request):
        empresas = Empresa.objects.all()
        part = []
        empresa_id = None
        decodigos = []

        empresa_id = request.POST.get('empresa_id')
            
        if empresa_id:
            try:
                empresa_id = int(empresa_id)
            except (ValueError, TypeError):
                empresa_id = None
                    
            decodigos = [
                    "111388", "112121", "112221", "112321", "112421", "112521", "112621", "112721",
                    "113241", "115291", "117017", "117018", "117661", "117662", "117664", "117665",
                    "122222", "122223", "122322", "122323", "122722", "122723", "127017", "127018",
                    "131185", "132121", "132221", "132321", "132421", "132521", "132721", "133241",
                    "137017", "137018", "137663", "137665", "147017", "147018", "152421", "157017",
                    "157018", "211128", "211142", "213151", "215291", "217017", "217661", "217662",
                    "217663", "217664", "221128", "221142", "221227", "221228", "223151", "225291",
                    "227017", "227661", "227662", "227663", "227664", "231128", "231227", "231228",
                    "235291", "237017", "237663", "237881", "247017", "257017", "261128", "261142",
                    "263151", "267017", "267661", "267662", "267663", "267664", "271128", "271142",
                    "271227", "271228", "273151", "275291", "277017", "277661", "277662", "277663",
                    "277664", "277881", "315291", "317017", "317661", "317662", "317664", "317771",
                    "317772", "317773", "317774", "317775", "317776", "321141", "325291", "327017",
                    "327018", "327661", "327664", "327771", "327772", "327773", "327774", "327775",
                    "327776", "335291", "337664", "337771", "337772", "337773", "337774", "337775",
                    "337776", "527996", "527997", "701111", "701112", "701116", "701119", "701211",
                    "701212", "701213", "701216", "701219", "701311", "701316", "701319", "701411",
                    "701416", "701419", "701512", "701516", "701519", "702116", "702212", "702216",
                    "702312", "702316", "702416", "702516", "702616", "702712", "702716", "703116",
                    "703211", "703212", "703216", "773178", "773278", "773378", "782381", "782781",
                ]
            
        if empresa_id:
                
            produtos = Produtos_notas.objects.filter(empresa_id=empresa_id).select_related('nota_titular')

            notas_ids = produtos.values_list('nota_titular', flat=True).distinct()
            notas_part_map = {
                np.id: np.part_titular_id
                for np in Notas_participantes.objects.filter(id__in=notas_ids)
            }

            participantes_ids = list(notas_part_map.values())
            participantes_map = {
                p.id: p.nome
                for p in Participantes.objects.filter(id__in=participantes_ids)
            }

            part = []
            for produto in produtos:
                    nota_id = getattr(produto.nota_titular, 'id', produto.nota_titular)  # depende como ForeignKey é usado
                    part_id = notas_part_map.get(nota_id)
                    nome_part = participantes_map.get(part_id, '') if part_id else ''
                    
                    part.append({
                        'nome': nome_part,
                        'cfop': produto.cfop_prod or '',
                        'codigo_lancamento': produto.cod_lancamento or '',
                    })


        return render(request, 'regras/regras.html', {
            'empresas': empresas,
            'part': part,
            'empresa_id': empresa_id,
            'decodigos': decodigos,
        })
                 