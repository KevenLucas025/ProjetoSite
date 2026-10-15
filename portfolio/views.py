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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from email.mime.image import MIMEImage
import mimetypes

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
        



def enviar_sugestao(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "status": "erro",
                "mensagem": "Método não permitido.",
            },
            status=405,
        )

    try:
        dados = json.loads(request.body)

        assunto = str(dados.get("assunto", "")).strip()
        nome = str(dados.get("nome", "")).strip()
        email_usuario = str(dados.get("email", "")).strip()
        mensagem = str(dados.get("mensagem", "")).strip()

        # Validar campos obrigatórios
        if not all([assunto, nome, email_usuario, mensagem]):
            return JsonResponse(
                {
                    "status": "erro",
                    "mensagem": "Preencha todos os campos.",
                },
                status=400,
            )

        # Validar e-mail do visitante
        try:
            validate_email(email_usuario)
        except ValidationError:
            return JsonResponse(
                {
                    "status": "erro",
                    "mensagem": "Informe um e-mail válido.",
                },
                status=400,
            )

        # Conteúdo em texto puro (alternativa ao HTML)
        corpo = (
            "Nova sugestão recebida pelo portfólio.\n\n"
            f"Assunto: {assunto}\n"
            f"Nome: {nome}\n"
            f"E-mail do visitante: {email_usuario}\n\n"
            f"Mensagem:\n{mensagem}"
        )

        # Localizar a imagem dentro de static/
        pasta_static = Path(settings.BASE_DIR) / "static"
        caminho_imagem = pasta_static / "imagem_navegador" / "logo_site.png"

        if not caminho_imagem.is_file():
            logger.warning("Imagem do e-mail não encontrada: %s", caminho_imagem)
            caminho_imagem = None
            
        # HTML da imagem: vazio caso o arquivo não seja encontrado
        imagem_html = ""

        
        if caminho_imagem:
            imagem_html = """
                <img
                    src="cid:imagem_navegador"
                    alt="Logo do portfólio"
                    style="display:block;width:100%;max-width:100%;height:auto;border-radius:12px;margin-bottom:24px;"
                >
            """

        # Montar o HTML do e-mail
        html_corpo = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nova sugestão recebida</title>
        </head>

        <body style="
            margin: 0;
            padding: 24px 10px;
            background-color: #f1f5f9;
            font-family: Arial, Helvetica, sans-serif;
            color: #1e293b;
        ">

            <div style="
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                border: 1px solid #e2e8f0;
            ">

                <div style="
                    background-color: #4dd0e1;
                    padding: 28px 24px;
                    text-align: center;
                ">
                    <h1 style="
                        margin: 0;
                        color: #CECFD2;
                        font-size: 24px;
                    ">
                        Nova sugestão recebida
                    </h1>

                    <p style="
                        margin: 10px 0 0;
                        color: #CECFD2;
                        font-size: 14px;
                    ">
                        Uma nova mensagem chegou pelo seu portfólio.
                    </p>
                </div>

                <div style="padding: 28px 24px;">

                    {imagem_html}

                    <p style="
                        margin: 0 0 8px;
                        color: #CECFD2;
                        font-size: 12px;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    ">
                        Assunto
                    </p>

                    <h2 style="
                        margin: 0 0 24px;
                        color: #CECFD2;
                        font-size: 21px;
                        overflow-wrap: anywhere;
                    ">
                        {escape(assunto)}
                    </h2>

                    <div style="
                        padding: 18px;
                        background-color: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 10px;
                        margin-bottom: 24px;
                    ">
                        <p style="margin: 0 0 12px; font-size: 14px;">
                            <strong>Nome:</strong>
                            {escape(nome)}
                        </p>

                        <p style="margin: 0; font-size: 14px;">
                            <strong>E-mail:</strong>
                            <a
                                href="mailto:{escape(email_usuario)}"
                                style="color: #047857; text-decoration: none;"
                            >
                                {escape(email_usuario)}
                            </a>
                        </p>
                    </div>

                    <h3 style="
                        margin: 0 0 12px;
                        font-size: 16px;
                        color: #CECFD2;
                    ">
                        Mensagem
                    </h3>

                    <div style="
                        padding: 18px;
                        background-color: #ffffff;
                        border-left: 4px solid #10b981;
                        border-radius: 4px;
                        color: #CECFD2;
                        font-size: 15px;
                        line-height: 1.7;
                        overflow-wrap: anywhere;
                    ">
                        {escape(mensagem).replace(chr(13), '').replace(chr(10), '<br>')}
                    </div>

                </div>

                <div style="
                    padding: 18px 24px;
                    background-color: #f8fafc;
                    border-top: 1px solid #e2e8f0;
                    text-align: center;
                ">
                    <p style="
                        margin: 0;
                        color: #CECFD2;
                        font-size: 12px;
                        line-height: 1.6;
                    ">
                        E-mail enviado automaticamente pelo formulário
                        de sugestões do portfólio.
                    </p>
                </div>

            </div>

        </body>
        </html>
        """

        # Criar a mensagem
        email_envio = EmailMultiAlternatives(
            subject=f"[Portfólio] {assunto}",
            body=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["sitepessoal2027@hotmail.com"],
            reply_to=[email_usuario],
        )

        # Anexar a versão HTML
        email_envio.attach_alternative(html_corpo, "text/html")

        # Incorporar a imagem no corpo do e-mail
        if caminho_imagem:
            mime_type, _ = mimetypes.guess_type(str(caminho_imagem))

            with caminho_imagem.open("rb") as arquivo:
                imagem = MIMEImage(
                    arquivo.read(),
                    _subtype=mime_type.split("/", 1)[1]
                )

            imagem.add_header("Content-ID", "<imagem_navegador>")
            imagem.add_header(
                "Content-Disposition",
                "inline",
                filename=caminho_imagem.name
            )

            email_envio.attach(imagem)


        # Enviar pelo Gmail
        email_envio.send(fail_silently=False)

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "erro",
                "mensagem": "Dados enviados em formato inválido.",
            },
            status=400,
        )

    except Exception:
        logger.exception("Erro ao enviar sugestão pelo Gmail.")

        return JsonResponse(
            {
                "status": "erro",
                "mensagem": "Não foi possível enviar a sugestão.",
            },
            status=500,
        )




