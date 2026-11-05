
import hashlib
import hmac
import json
import os
import time

from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import WebhookEvento


BASE_DIR = Path(settings.BASE_DIR)
load_dotenv(BASE_DIR / ".env")


def validar_assinatura(request):
    timestamp = request.headers.get("X-Cakto-Timestamp", "")
    assinatura = request.headers.get("X-Cakto-Signature", "")

    if not timestamp or not assinatura:
        return False

    try:
        instante = int(timestamp)
    except (ValueError, TypeError):
        return False

    if abs(time.time() - instante) > 300:
        return False

    corpo = request.body

    for codigo in ["F", "W", "L", "G"]:
        segredo = os.getenv(f"CAKTO_SECRET_{codigo}", "")

        if not segredo:
            continue

        mensagem = timestamp.encode() + b"." + corpo

        esperado = hmac.new(
            segredo.encode(),
            mensagem,
            hashlib.sha256
        ).hexdigest()

        assinatura_esperada = f"v1={esperado}"

        if hmac.compare_digest(
            assinatura,
            assinatura_esperada
        ):
            return True

    return False


@csrf_exempt
def receber_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {"erro": "Método não permitido"},
            status=405
        )

    if not validar_assinatura(request):
        return JsonResponse(
            {"erro": "Assinatura inválida"},
            status=401
        )

    try:
        dados = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"erro": "JSON inválido"},
            status=400
        )

    evento = str(dados.get("event", ""))
    informacoes = dados.get("data") or {}

    pedido_id = str(informacoes.get("id", ""))

    identificador = hashlib.sha256(
        request.body
    ).hexdigest()

    WebhookEvento.objects.get_or_create(
        identificador=identificador,
        defaults={
            "evento": evento,
            "pedido_id": pedido_id,
            "payload": request.body.decode("utf-8"),
        }
    )

    return JsonResponse({
        "recebido": True,
        "evento": evento
    })
