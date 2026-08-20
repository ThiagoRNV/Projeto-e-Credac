from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Apenas se quiser customizar a listagem do User
class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

# Registrar User com o admin customizado
admin.site.unregister(User)           # primeiro desregistrar o User padrão
admin.site.register(User, MyUserAdmin)
    