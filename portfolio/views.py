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
import hashlib
import hmac
import secrets

from django.http import HttpResponseForbidden

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

            # Gera uma chave exclusiva para este comentário.
            token = secrets.token_urlsafe(32)

            comentario = form.save(commit=False)
            comentario.token_edicao_hash = hashlib.sha256(
                token.encode("utf-8")
            ).hexdigest()
            comentario.save()
            form.save_m2m()

            notificar_novo_comentario(comentario)

            resposta = redirect("comentarios")
            resposta.set_cookie(
                key=f"comentario_edicao_{comentario.pk}",
                value=token,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                secure=request.is_secure(),
                samesite="Lax",
                path="/",
            )
            return resposta

    else:
        form = ComentarioForm()

    # Todos os comentários continuam visíveis publicamente.
    lista_comentarios = list(
        Comentario.objects.all().order_by("-criado_em")
    )

    # Identifica os comentários editáveis neste navegador.
    comentarios_editaveis = []

    for item in lista_comentarios:
        token_cookie = request.COOKIES.get(
            f"comentario_edicao_{item.pk}", ""
        )

        if not token_cookie or not item.token_edicao_hash:
            continue

        hash_token = hashlib.sha256(
            token_cookie.encode("utf-8")
        ).hexdigest()

        if hmac.compare_digest(hash_token, item.token_edicao_hash):
            comentarios_editaveis.append(item.pk)

    return render(
        request,
        "comentarios.html",
        {
            "form": form,
            "comentarios": lista_comentarios,
            "comentarios_editaveis": comentarios_editaveis,
            "enviado": request.GET.get("enviado") == "1",
        },
    )

    

def editar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)

    token_cookie = request.COOKIES.get(
        f"comentario_edicao_{comentario.pk}", ""
    )

    if not token_cookie or not comentario.token_edicao_hash:
        return JsonResponse(
            {"sucesso": False, "erro": "Sem permissão para editar."},
            status=403,
        )

    hash_token = hashlib.sha256(
        token_cookie.encode("utf-8")
    ).hexdigest()

    if not hmac.compare_digest(
        hash_token, comentario.token_edicao_hash
    ):
        return JsonResponse(
            {"sucesso": False, "erro": "Token de edição inválido."},
            status=403,
        )

    if request.method != "POST":
        return JsonResponse(
            {"sucesso": False, "erro": "Método não permitido."},
            status=405,
        )

    form = ComentarioForm(request.POST, instance=comentario)

    if not form.is_valid():
        return JsonResponse(
            {
                "sucesso": False,
                "erros": form.errors.get_json_data(),
            },
            status=400,
        )

    if form.cleaned_data.get("website"):
        return JsonResponse(
            {"sucesso": False, "erro": "Envio inválido."},
            status=400,
        )

    comentario = form.save()

    return JsonResponse({
        "sucesso": True,
        "nome": comentario.nome,
        "texto": comentario.texto,
        "avaliacao": comentario.avaliacao,
        "tipo": comentario.get_tipo_display(),
        "editado": comentario.editado,
        "editado_em": (
            comentario.editado_em.strftime("%d/%m/%Y %H:%M")
            if comentario.editado_em else ""
        ),
    })

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