from django.shortcuts import render
from .models import Projeto
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.conf import settings
import json
import traceback


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


@csrf_exempt
def enviar_sugestao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            nome = data.get('nome')
            email_usuario = data.get('email')
            assunto = data.get('assunto')
            mensagem = data.get('mensagem')

            email = EmailMultiAlternatives(
                subject='Teste',
                body='Teste simples',
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
            )

            email.send(fail_silently=False)

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            print("ERRO COMPLETO:")
            traceback.print_exc()

            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'status': 'erro'})