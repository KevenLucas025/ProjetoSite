
import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def autorizar_gmail():
    credenciais = None

    if os.path.exists("token.json"):
        credenciais = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES,
        )

    if not credenciais or not credenciais.valid:
        if credenciais and credenciais.expired and credenciais.refresh_token:
            credenciais.refresh(Request())
        else:
            fluxo = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            credenciais = fluxo.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as arquivo:
            arquivo.write(credenciais.to_json())

    servico = build("gmail", "v1", credentials=credenciais)
    perfil = servico.users().getProfile(userId="me").execute()

    print("Autorização concluída!")
    print("Conta Gmail:", perfil["emailAddress"])


if __name__ == "__main__":
    autorizar_gmail()
