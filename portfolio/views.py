from django.shortcuts import render
from .models import Projeto
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
import json


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


def enviar_sugestao(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)

        email_usuario = data.get('email')
        mensagem = data.get('mensagem')


        send_mail(
            subject='📩 Nova sugestão do site',
            message=f'Email do usuário: {email_usuario}\n\nSugestão:\n{mensagem}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
        )
        

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'erro'})