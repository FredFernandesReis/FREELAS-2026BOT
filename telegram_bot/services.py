
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# Localiza a pasta principal do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env.
load_dotenv(BASE_DIR / ".env")

# Token do bot do Telegram.
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def telegram_request(method, data=None, timeout=35):
    if not TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN não foi configurado no arquivo .env"
        )

    url = f"{BASE_URL}/{method}"

    response = requests.post(
        url,
        json=data or {},
        timeout=timeout
    )

    response.raise_for_status()

    resultado = response.json()

    if not resultado.get("ok"):
        raise Exception(
            resultado.get("description", "Erro no Telegram")
        )

    return resultado["result"]


def enviar_mensagem(chat_id, texto, teclado=None):
    dados = {
        "chat_id": chat_id,
        "text": texto
    }

    if teclado:
        dados["reply_markup"] = teclado

    return telegram_request("sendMessage", dados)


def responder_botao(callback_id):
    return telegram_request(
        "answerCallbackQuery",
        {"callback_query_id": callback_id}
    )


def criar_link_convite(expiracao_horas=24):
    import os
    import time

    canal_id = os.getenv("TELEGRAM_CHANNEL_ID")

    if not canal_id:
        raise ValueError(
            "TELEGRAM_CHANNEL_ID não configurado no .env"
        )

    dados = {
        "chat_id": canal_id,
        "member_limit": 1,
        "expire_date": int(time.time()) + (expiracao_horas * 3600),
    }

    resultado = telegram_request(
        "createChatInviteLink",
        dados
    )

    return resultado["invite_link"]
