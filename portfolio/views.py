from django.shortcuts import render
from .models import Projeto

def home(request):
    destaques = Projeto.objects.filter(ativo=True, destaque=True)[:6]
    return render(request, "home.html", {"destaques": destaques})

def sobre(request):
    return render(request, "sobre.html")

def projetos(request):
    itens = Projeto.objects.filter(ativo=True)
    return render(request, "projetos.html", {"projetos": itens})

def contato(request):
    return render(request, "contato.html")