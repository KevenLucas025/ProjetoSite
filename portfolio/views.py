from django.shortcuts import render
from .models import Projeto
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
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


@csrf_exempt
def enviar_sugestao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            nome = data.get('nome')
            email_usuario = data.get('email')
            assunto = data.get('assunto')
            mensagem = data.get('mensagem')

            subject = '📩 Nova sugestão recebida do site'

            text_content = f'''
Nova sugestão recebida

Nome: {nome}
Email: {email_usuario}
Assunto: {assunto}

Mensagem:
{mensagem}
            '''

            html_content = f"""
            <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 20px; border-radius: 10px;">
                    
                    <h2 style="color: #333;">📩 Nova Sugestão Recebida</h2>
                    
                    <hr style="border: none; border-top: 1px solid #eee;">

                    <p><strong>👤 Nome:</strong> {nome}</p>
                    <p><strong>📧 Email:</strong> {email_usuario}</p>
                    <p><strong>📝 Assunto:</strong> {assunto}</p>

                    <div style="margin-top: 20px;">
                        <p><strong>💬 Mensagem:</strong></p>
                        <p style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
                            {mensagem}
                        </p>
                    </div>

                    <hr style="border: none; border-top: 1px solid #eee; margin-top: 20px;">

                    <p style="font-size: 12px; color: #777;">
                        Enviado automaticamente pelo meu site 🚀
                    </p>

                </div>
            </div>
            """

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            print("ERRO REAL:", e)
            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'status': 'erro'})