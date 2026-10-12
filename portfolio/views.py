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
from django.shortcuts import render, redirect,get_object_or_404
from .models import Comentario
from .forms import ComentarioForm
import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def home(request):
    destaques = Projeto.objects.filter(ativo=True, destaque=True)[:6]
    return render(request, "home.html", {"destaques": destaques})


def sobre(request):
    return render(request, "sobre.html")


def projetos(request):
    itens = Projeto.objects.filter(ativo=True)
    
    context = {
        "projetos": itens,
        "total_projetos": itens.count(),
    }
    
    return render(request, "projetos.html", context)


def contato(request):
    return render(request, "contato.html")



def comentarios(request):
    if request.method == "POST":
        form = ComentarioForm(request.POST)

        if form.is_valid():
            # Bloqueia envios automáticos pelo campo-armadilha.
            if form.cleaned_data.get("website"):
                return redirect("comentarios")

            comentario = form.save()
            notificar_novo_comentario(comentario)
            return redirect("comentarios")

    else:
        form = ComentarioForm()

    # Nunca envia críticas e sugestões para a página pública.
    comentarios = Comentario.objects.all().order_by("-criado_em")

    return render(
        request,
        "comentarios.html",
        {
            "form": form,
            "comentarios": comentarios,
            "enviado": request.GET.get("enviado") == "1",
        },
    )
    
def editar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)

    if request.method == "POST":
        form = ComentarioForm(request.POST, instance=comentario)

        if form.is_valid():
            if form.cleaned_data.get("website"):
                return redirect("comentarios")

            form.save()
            return redirect("comentarios")
    else:
        form = ComentarioForm(instance=comentario)

    return render(
        request,
        "editar_comentario.html",
        {
            "form": form,
            "comentario": comentario,
        },
    )
def notificar_novo_comentario(comentario):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        logger.warning("Telegram não configurado.")
        return

    
    mensagem = (
        "🔔 <b>NOVO COMENTÁRIO NO PORTFÓLIO</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Nome:</b> {comentario.nome}\n"
        f"📌 <b>Tipo:</b> {comentario.get_tipo_display()}\n"
        f"⭐ <b>Avaliação:</b> {comentario.avaliacao}/5\n\n"
        "💬 <b>Comentário:</b>\n"
        f"<blockquote>{comentario.texto}</blockquote>\n\n"
        f"🕒 <b>Data:</b> {comentario.criado_em:%d/%m/%Y %H:%M}\n"
        "━━━━━━━━━━━━━━━━━━"
    )


    try:
        resposta = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": mensagem,
                "parse_mode": "HTML",
            },
            timeout=5,
        )
        resposta.raise_for_status()

        if not resposta.json().get("ok"):
            logger.warning("Telegram não confirmou o envio.")

    except (requests.RequestException, ValueError):
        logger.exception("Falha ao enviar notificação ao Telegram.")