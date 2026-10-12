from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sobre/", views.sobre, name="sobre"),
    path("projetos/", views.projetos, name="projetos"),
    path("contato/", views.contato, name="contato"),
    path("comentarios/", views.comentarios, name="comentarios"),
    path("comentarios/<int:pk>/editar/",views.editar_comentario,name="editar_comentario",),
]