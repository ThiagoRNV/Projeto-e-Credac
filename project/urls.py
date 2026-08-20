from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from django.conf.urls.static import static # type: ignore
from django.conf import settings # type: ignore
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from accounts.views import CustomLoginView

urlpatterns = [
    # path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('login')),    

    path('home/', include('home.urls')),       

    path('gerarArquivo/', include('gerar_arquivo.urls')),

    path('menu_fichas/', include('gerar_fichas.urls.menu')),
    path('fichas1/', include('gerar_fichas.urls.fichas1')),
    path('fichas2/', include('gerar_fichas.urls.fichas2')),
    path('fichas3/', include('gerar_fichas.urls.fichas3')),
    path('fichas4/', include('gerar_fichas.urls.fichas4')),
    path('fichas5/', include('gerar_fichas.urls.fichas5')),
    path('fichas6/', include('gerar_fichas.urls.fichas6')),

    path('historico/', include('historico.urls')),

    path('cadastro_empresa/', include('cadastro.urls.empresa')),
    path('cadastro_produto/', include('cadastro.urls.produto')),
    path('cadastro_listagem/', include('cadastro.urls.listagem')),
    path('regras_cod_lan/', include('cadastro.urls.regras_cod_lan')),

    path('sped/', include('metodo_rateio.urls.sped')),
    path('planilha/', include('metodo_rateio.urls.planilha')),


    path('validacao_dados/', include('validacao.urls.outros_modelos.painel_de_controle')),
    path('validacao_dados/', include('validacao.urls.outros_modelos.processamento')),
    path('validacao_dados/', include('validacao.urls.outros_modelos.view_data')),

    path('validacao_dados/', include('validacao.urls.nfe.painel_de_controlenfe')),
    path('validacao_dados/', include('validacao.urls.nfe.processamento')),
    path('validacao_dados/', include('validacao.urls.nfe.view_data')),
    path('upload/', include('validacao.urls.uploads.uploads')),

    path('pendencias/', include('pendencias.urls')),

    path('ajuda/', include('help.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
