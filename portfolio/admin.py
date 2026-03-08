from django.contrib import admin
from .models import Projeto

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ativo", "destaque", "ordem")
    list_filter = ("ativo", "destaque")
    search_fields = ("titulo", "descricao", "tecnologias")
    ordering = ("ordem", "-destaque", "-id")