from django.contrib import admin
from .models import Projeto
from .models import Comentario


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ativo", "destaque", "ordem")
    list_filter = ("ativo", "destaque")
    search_fields = ("titulo", "descricao", "tecnologias")
    ordering = ("ordem", "-destaque", "-id")
    


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo",
        "avaliacao",
        "publico",
        "editado",
        "editado_em",
        "criado_em",
    )

    list_filter = (
        "tipo",
        "publico",
        "editado",
        "avaliacao",
        "criado_em",
    )

    search_fields = ("nome", "texto")

    readonly_fields = (
        "publico",
        "editado",
        "editado_em",
        "criado_em",
    )

    ordering = ("-criado_em",)
