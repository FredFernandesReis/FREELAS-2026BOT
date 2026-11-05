
import time
import os
import re

from django.core.management.base import BaseCommand

from telegram_bot.services import (
    telegram_request,
    enviar_mensagem,
    responder_botao,
)

from clientes.models import Cliente
from assinaturas.models import Assinatura


ADMINISTRADORES = {
    "F": "FREELANCER (F)",
    "W": "FREELANCER (W)",
    "L": "FREELANCER (L)",
    "G": "FREELANCER (G)",
}


class Command(BaseCommand):
    help = "Inicia o bot do Freelancer BH Região"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando bot...")

        bot = telegram_request("getMe")

        self.stdout.write(
            self.style.SUCCESS(
                f"Bot conectado: @{bot['username']}"
            )
        )

        webhook = telegram_request("getWebhookInfo")

        if webhook.get("url"):
            self.stdout.write(
                self.style.ERROR(
                    "Existe um webhook configurado no Telegram."
                )
            )
            return

        offset = None

        self.stdout.write("Aguardando mensagens...")

        while True:
            try:
                dados = {"timeout": 25}

                if offset is not None:
                    dados["offset"] = offset

                atualizacoes = telegram_request(
                    "getUpdates",
                    dados,
                    timeout=35
                )

                for atualizacao in atualizacoes:
                    offset = atualizacao["update_id"] + 1

                    try:
                        self.processar_atualizacao(atualizacao)
                    except Exception as erro:
                        self.stderr.write(str(erro))

            except Exception as erro:
                self.stderr.write(str(erro))
                time.sleep(3)

    def registrar_cliente(self, usuario, codigo=""):
        telegram_id = usuario["id"]

        nome = usuario.get("first_name", "")
        sobrenome = usuario.get("last_name", "")
        nome_completo = f"{nome} {sobrenome}".strip()
        username = usuario.get("username", "")

        cliente, criado = Cliente.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "nome": nome_completo,
                "username": username,
                "administrador": codigo,
            }
        )

        if not criado:
            cliente.nome = nome_completo
            cliente.username = username

            campos = ["nome", "username", "atualizado_em"]

            if not cliente.administrador and codigo in ADMINISTRADORES:
                cliente.administrador = codigo
                campos.append("administrador")

            cliente.save(update_fields=campos)

        return cliente

    def processar_atualizacao(self, atualizacao):
        mensagem = atualizacao.get("message")

        if mensagem:
            chat_id = mensagem["chat"]["id"]
            usuario = mensagem.get("from", {})
            texto = mensagem.get("text", "").strip()

            # Comando /start
            if texto.startswith("/start"):
                partes = texto.split(maxsplit=1)

                codigo = (
                    partes[1].upper()
                    if len(partes) > 1
                    else ""
                )

                if codigo not in ADMINISTRADORES:
                    codigo = ""

                cliente = self.registrar_cliente(usuario, codigo)

                if cliente.administrador:
                    self.solicitar_email(chat_id, cliente)
                else:
                    self.mostrar_menu(chat_id)

                return

            cliente = Cliente.objects.filter(
                telegram_id=usuario.get("id")
            ).first()

            # Comando /menu
            if texto == "/menu":
                if not cliente:
                    enviar_mensagem(
                        chat_id,
                        "Digite /start para começar seu cadastro."
                    )
                    return

                if cliente.aguardando_email:
                    enviar_mensagem(
                        chat_id,
                        "📧 Primeiro, informe seu e-mail para continuar."
                    )
                    return

                self.mostrar_menu_cliente(chat_id)
                return

            # Cliente está cadastrando e-mail
            if cliente and cliente.aguardando_email:
                self.processar_email(chat_id, cliente, texto)
                return

            enviar_mensagem(
                chat_id,
                "Digite /start para começar ou /menu para abrir o menu."
            )
            return

        # Botões do Telegram
        callback = atualizacao.get("callback_query")

        if callback:
            responder_botao(callback["id"])

            chat_id = callback["message"]["chat"]["id"]
            usuario = callback.get("from", {})
            escolha = callback.get("data", "")

            # Seleção do administrador
            if escolha.startswith("admin_"):
                codigo = escolha.replace("admin_", "")

                if codigo in ADMINISTRADORES:
                    cliente = self.registrar_cliente(usuario, codigo)

                    if cliente.administrador:
                        self.solicitar_email(chat_id, cliente)
                    else:
                        self.mostrar_menu(chat_id)

                return

            cliente = Cliente.objects.filter(
                telegram_id=usuario.get("id")
            ).first()

            if not cliente:
                enviar_mensagem(
                    chat_id,
                    "Você ainda não está cadastrado. Digite /start."
                )
                return

            # Meu cadastro
            if escolha == "menu_cadastro":
                texto = (
                    "👤 MEU CADASTRO\n\n"
                    f"Nome: {cliente.nome}\n"
                    f"Usuário: @{cliente.username or 'Não informado'}\n"
                    f"E-mail: {cliente.email or 'Não cadastrado'}\n"
                    f"Administrador: "
                    f"{ADMINISTRADORES.get(cliente.administrador, 'Não definido')}"
                )

                enviar_mensagem(chat_id, texto)
                self.mostrar_menu_cliente(chat_id)
                return

            # Minha assinatura
            if escolha == "menu_assinatura":
                assinatura = cliente.assinaturas.order_by(
                    "-criado_em"
                ).first()

                if not assinatura:
                    enviar_mensagem(
                        chat_id,
                        "💳 Você ainda não possui uma assinatura cadastrada.\n\n"
                        "Quando seu pagamento for confirmado, "
                        "sua assinatura aparecerá aqui."
                    )
                else:
                    vencimento = (
                        assinatura.vencimento.strftime("%d/%m/%Y")
                        if assinatura.vencimento
                        else "Ainda não definido"
                    )

                    texto = (
                        "💳 MINHA ASSINATURA\n\n"
                        f"Status: {assinatura.get_status_display()}\n"
                        f"Valor: R$ {assinatura.valor}\n"
                        f"Vencimento: {vencimento}"
                    )

                    enviar_mensagem(chat_id, texto)

                self.mostrar_menu_cliente(chat_id)
                return

            # Renovar assinatura
            if escolha == "menu_renovar":
                self.mostrar_pagamento(
                    chat_id,
                    cliente.administrador
                )
                self.mostrar_menu_cliente(chat_id)
                return

            # Suporte
            if escolha == "menu_suporte":
                enviar_mensagem(
                    chat_id,
                    "🆘 SUPORTE\n\n"
                    "Precisa de ajuda com sua assinatura?\n\n"
                    "Entre em contato com o atendimento "
                    "do Freelancer BH Região."
                )

                self.mostrar_menu_cliente(chat_id)
                return

            # Voltar ao menu
            if escolha == "menu_inicio":
                self.mostrar_menu_cliente(chat_id)
                return

    def mostrar_menu(self, chat_id):
        teclado = {
            "inline_keyboard": [
                [{"text": "FREELANCER (F)", "callback_data": "admin_F"}],
                [{"text": "FREELANCER (W)", "callback_data": "admin_W"}],
                [{"text": "FREELANCER (L)", "callback_data": "admin_L"}],
                [{"text": "FREELANCER (G)", "callback_data": "admin_G"}],
            ]
        }

        texto = (
            "👋 Olá! Seja bem-vindo ao Freelancer BH Região!\n\n"
            "Aqui você terá acesso às oportunidades de trabalho "
            "divulgadas em nossa comunidade.\n\n"
            "💰 Assinatura mensal: R$ 14,99\n\n"
            "Selecione o administrador que está atendendo você:"
        )

        enviar_mensagem(chat_id, texto, teclado)

    def mostrar_menu_cliente(self, chat_id):
        teclado = {
            "inline_keyboard": [
                [
                    {
                        "text": "👤 Meu cadastro",
                        "callback_data": "menu_cadastro"
                    }
                ],
                [
                    {
                        "text": "💳 Minha assinatura",
                        "callback_data": "menu_assinatura"
                    }
                ],
                [
                    {
                        "text": "🔄 Renovar assinatura",
                        "callback_data": "menu_renovar"
                    }
                ],
                [
                    {
                        "text": "🆘 Suporte",
                        "callback_data": "menu_suporte"
                    }
                ],
            ]
        }

        texto = (
            "🏠 MENU DO CLIENTE\n\n"
            "Bem-vindo ao Freelancer BH Região!\n\n"
            "Escolha uma opção abaixo:"
        )

        enviar_mensagem(chat_id, texto, teclado)

    def solicitar_email(self, chat_id, cliente):
        if cliente.email:
            cliente.aguardando_email = False
            cliente.save(update_fields=["aguardando_email"])

            self.mostrar_pagamento(
                chat_id,
                cliente.administrador
            )

            self.mostrar_menu_cliente(chat_id)
            return

        cliente.aguardando_email = True
        cliente.save(update_fields=["aguardando_email"])

        enviar_mensagem(
            chat_id,
            "📧 Antes de continuar, precisamos do seu e-mail.\n\n"
            "Digite abaixo o mesmo endereço de e-mail que você "
            "vai utilizar na compra pela Cakto.\n\n"
            "⚠️ É importante informar o e-mail correto para "
            "identificarmos seu pagamento e liberar seu acesso."
        )

    def processar_email(self, chat_id, cliente, email):
        email = email.strip().lower()

        padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(padrao, email):
            enviar_mensagem(
                chat_id,
                "❌ Esse e-mail parece inválido.\n\n"
                "Digite novamente um endereço válido."
            )
            return

        cliente.email = email
        cliente.aguardando_email = False

        cliente.save(
            update_fields=["email", "aguardando_email", "atualizado_em"]
        )

        enviar_mensagem(
            chat_id,
            "✅ E-mail cadastrado com sucesso!\n\n"
            "Agora você pode continuar para o pagamento."
        )

        self.mostrar_pagamento(
            chat_id,
            cliente.administrador
        )

        self.mostrar_menu_cliente(chat_id)

    def mostrar_pagamento(self, chat_id, codigo):
        links = {
            "F": os.getenv("CAKTO_LINK_F", ""),
            "W": os.getenv("CAKTO_LINK_W", ""),
            "L": os.getenv("CAKTO_LINK_L", ""),
            "G": os.getenv("CAKTO_LINK_G", ""),
        }

        nome = ADMINISTRADORES.get(codigo, "ADMINISTRADOR")
        link = links.get(codigo, "")

        if not link:
            enviar_mensagem(
                chat_id,
                f"Você foi direcionado para {nome}!\n\n"
                "O pagamento deste administrador ainda está "
                "sendo configurado. Entre em contato com o atendimento."
            )
            return

        enviar_mensagem(
            chat_id,
            f"Você foi direcionado para {nome}!\n\n"
            "💰 Assinatura mensal: R$ 14,99\n\n"
            "📧 Utilize no checkout o mesmo e-mail cadastrado "
            "aqui no Telegram.\n\n"
            "Clique no link abaixo para realizar sua assinatura:\n\n"
            f"{link}"
        )
