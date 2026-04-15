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
            
            email_usuario = data.get('email')
            mensagem = data.get('mensagem')

            send_mail(
                subject='📩 Nova sugestão recebi do site',
                message=f'Email do usuário: {email_usuario}\n\nSugestão:\n{mensagem}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,  
            )

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            print("ERRO COMPLETO:")
            traceback.print_exc()

            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'status': 'erro'})