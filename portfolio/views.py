from django.shortcuts import render
from .models import Projeto
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
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
            
            assunto_user = data.get('assunto', 'Sem Assunto')
            nome_user = data.get('nome', 'Anônimo')
            email_usuario = data.get('email')
            mensagem = data.get('mensagem')

            # 1. Configuração do Assunto e Destinatários
            subject = f'📩 Nova Sugestão: {assunto_user}'
            from_email = settings.EMAIL_HOST_USER
            to = [settings.EMAIL_HOST_USER]

            # 2. O corpo do e-mail em HTML com CSS Inline (melhor compatibilidade)
            html_content = f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; background-color: #ffffff;">
                <div style="background: linear-gradient(135deg, #4dd0e1, #22d3ee); padding: 20px; text-align: center;">
                    <h1 style="margin: 0; color: #000000; font-size: 24px;">Nova Sugestão Recebida</h1>
                </div>
                <div style="padding: 30px; color: #374151; line-height: 1.6;">
                    <p style="margin-top: 0;">Você recebeu uma nova mensagem através do seu portfólio:</p>
                    <hr style="border: 0; border-top: 1px solid #f3f4f6; margin: 20px 0;">
                    
                    <p><strong>👤 Nome:</strong> {nome_user}</p>
                    <p><strong>📧 E-mail:</strong> <a href="mailto:{email_usuario}" style="color: #0ea5e9;">{email_usuario}</a></p>
                    <p><strong>📝 Assunto:</strong> {assunto_user}</p>
                    
                    <div style="background-color: #f9fafb; padding: 15px; border-left: 4px solid #4dd0e1; margin-top: 20px; border-radius: 4px;">
                        <p style="margin-top: 0; font-weight: bold; color: #111827;">Mensagem:</p>
                        <p style="margin-bottom: 0; white-space: pre-wrap;">{mensagem}</p>
                    </div>
                </div>
                <div style="background-color: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #9ca3af;">
                    Este é um e-mail automático gerado pelo seu Portfólio Python.
                </div>
            </div>
            """

            # 3. Criar a versão em texto puro para fallback
            text_content = strip_tags(html_content)

            # 4. Montar e enviar o e-mail
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            print("ERRO COMPLETO:")
            traceback.print_exc()
            return JsonResponse({'erro': str(e), 'detalhe': 'Erro interno ao processar e-mail'}, status=500)

    return JsonResponse({'status': 'erro'})