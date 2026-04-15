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
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8; padding:20px; font-family:Arial, sans-serif;">
                <tr>
                    <td align="center">
                    
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:10px; overflow:hidden;">
                        
                        <!-- HEADER -->
                        <tr>
                        <td style="background:#202124; padding:20px; text-align:center;">
                            <img src="https://projetosite-z4ap.onrender.com/static/imagem_navegador/logo_site.png" width="120" style="margin-bottom:10px;">
                            <h2 style="margin:0; color:#ffffff;">Nova Sugestão Recebida</h2>
                        </td>
                        </tr>

                        <!-- BODY -->
                        <tr>
                        <td style="padding:25px; color:#333;">
                            
                            <p style="margin-top:0;">Você recebeu uma nova mensagem do seu portfólio:</p>

                            <table width="100%" cellpadding="10" cellspacing="0" style="margin-top:15px; border:1px solid #eee; border-radius:8px;">
                            <tr>
                                <td><strong>👤 Nome:</strong></td>
                                <td>{nome_user}</td>
                            </tr>
                            <tr>
                                <td><strong>📧 Email:</strong></td>
                                <td><a href="mailto:{email_usuario}">{email_usuario}</a></td>
                            </tr>
                            <tr>
                                <td><strong>📝 Assunto:</strong></td>
                                <td>{assunto_user}</td>
                            </tr>
                            </table>

                            <!-- MENSAGEM -->
                            <div style="margin-top:20px;">
                            <p><strong>💬 Mensagem:</strong></p>
                            <div style="background:#f9fafb; padding:15px; border-left:4px solid #22d3ee;">
                                {mensagem}
                            </div>
                            </div>

                        </td>
                        </tr>

                        <!-- FOOTER -->
                        <tr>
                        <td style="background:#f1f1f1; text-align:center; padding:15px; font-size:12px; color:#777;">
                            Enviado automaticamente pelo seu site 🚀
                        </td>
                        </tr>

                    </table>

                    </td>
                </tr>
                </table>
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