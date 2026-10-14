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
import os
from pathlib import Path
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


# ==========================================================
# ARMAZENAMENTO DE COMENTÁRIOS
# Local: db.sqlite3
# Render: comentarios.json
# ==========================================================

def usar_json_comentarios():
    return (
        os.environ.get("RENDER", "").lower() == "true"
        or os.environ.get("COMENTARIOS_JSON", "").lower() == "true"
    )


ARQUIVO_COMENTARIOS = Path(settings.BASE_DIR) / "comentarios.json"


def ler_comentarios_json():
    if not ARQUIVO_COMENTARIOS.exists():
        return []

    try:
        with ARQUIVO_COMENTARIOS.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            raise ValueError("O arquivo de comentários deve conter uma lista.")

        return dados

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        logger.exception("Erro ao ler comentarios.json.")
        raise


def salvar_comentarios_json(comentarios):
    temporario = ARQUIVO_COMENTARIOS.with_suffix(".tmp")

    with temporario.open("w", encoding="utf-8") as arquivo:
        json.dump(
            comentarios,
            arquivo,
            ensure_ascii=False,
            indent=4,
        )

    # Substitui o arquivo somente depois de concluir a escrita.
    temporario.replace(ARQUIVO_COMENTARIOS)


class ComentarioJSON:
    TIPOS = {
        "elogio": "Elogio",
        "sugestao": "Sugestão",
        "critica": "Crítica ou reclamação",
    }

    def __init__(self, dados):
        self.pk = dados["id"]
        self.id = dados["id"]
        self.nome = dados["nome"]
        self.texto = dados["texto"]
        self.avaliacao = int(dados["avaliacao"])
        self.tipo = dados["tipo"]
        self.publico = dados.get("publico", True)
        self.editado = dados.get("editado", False)
        self.token_edicao_hash = dados.get("token_edicao_hash", "")

        self.criado_em = datetime.fromisoformat(dados["criado_em"])

        editado_em = dados.get("editado_em")
        self.editado_em = (
            datetime.fromisoformat(editado_em)
            if editado_em else None
        )

    def get_tipo_display(self):
        return self.TIPOS.get(self.tipo, self.tipo)

    def to_dict(self):
        return {
            "id": self.pk,
            "nome": self.nome,
            "texto": self.texto,
            "avaliacao": self.avaliacao,
            "tipo": self.tipo,
            "publico": self.publico,
            "editado": self.editado,
            "editado_em": (
                self.editado_em.isoformat()
                if self.editado_em else None
            ),
            "token_edicao_hash": self.token_edicao_hash,
            "criado_em": self.criado_em.isoformat(),
        }



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
            if form.cleaned_data.get("website"):
                return redirect("comentarios")

            token = secrets.token_urlsafe(32)
            agora = timezone.now()

            if usar_json_comentarios():
                registros = ler_comentarios_json()

                novo_id = max(
                    (int(item["id"]) for item in registros),
                    default=0,
                ) + 1

                comentario = ComentarioJSON({
                    "id": novo_id,
                    "nome": form.cleaned_data["nome"],
                    "texto": form.cleaned_data["texto"],
                    "avaliacao": form.cleaned_data["avaliacao"],
                    "tipo": form.cleaned_data["tipo"],
                    "publico": True,
                    "editado": False,
                    "editado_em": None,
                    "token_edicao_hash": hashlib.sha256(
                        token.encode("utf-8")
                    ).hexdigest(),
                    "criado_em": agora.isoformat(),
                })

                registros.append(comentario.to_dict())
                salvar_comentarios_json(registros)

            else:
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

    if usar_json_comentarios():
        registros = ler_comentarios_json()

        lista_comentarios = [
            ComentarioJSON(item)
            for item in registros
            if item.get("publico", True)
        ]

        lista_comentarios.sort(
            key=lambda item: item.criado_em,
            reverse=True,
        )

    else:
        lista_comentarios = list(
            Comentario.objects.filter(publico=True).order_by("-criado_em")
        )

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
    usando_json = usar_json_comentarios()
    registro = None

    if usando_json:
        registros = ler_comentarios_json()

        registro = next(
            (
                item for item in registros
                if int(item["id"]) == int(pk)
            ),
            None,
        )

        if registro is None:
            return JsonResponse(
                {"sucesso": False, "erro": "Comentário não encontrado."},
                status=404,
            )

        comentario = ComentarioJSON(registro)

    else:
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

    form = ComentarioForm(
        request.POST,
        instance=None if usando_json else comentario,
    )

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

    if usando_json:
        campos = {
            "nome": form.cleaned_data["nome"],
            "texto": form.cleaned_data["texto"],
            "avaliacao": form.cleaned_data["avaliacao"],
            "tipo": form.cleaned_data["tipo"],
        }

        houve_alteracao = any(
            str(registro[campo]) != str(valor)
            for campo, valor in campos.items()
        )

        registro.update(campos)

        if houve_alteracao:
            registro["editado"] = True
            registro["editado_em"] = timezone.now().isoformat()

        salvar_comentarios_json(registros)
        comentario = ComentarioJSON(registro)

    else:
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