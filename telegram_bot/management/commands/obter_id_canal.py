
from django.core.management.base import BaseCommand
from telegram_bot.services import telegram_request


class Command(BaseCommand):
    help = "Descobre o ID numérico do canal do Telegram"

    def handle(self, *args, **options):
        self.stdout.write("Procurando mensagens recebidas...")

        atualizacoes = telegram_request(
            "getUpdates",
            {"timeout": 0}
        )

        encontrou = False

        for atualizacao in atualizacoes:
            mensagem = (
                atualizacao.get("channel_post")
                or atualizacao.get("edited_channel_post")
            )

            if mensagem:
                chat = mensagem.get("chat", {})

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Canal encontrado: {chat.get('title')}"
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"ID DO CANAL: {chat.get('id')}"
                    )
                )

                encontrou = True

        if not encontrou:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhuma publicação do canal encontrada. "
                    "Confira se o bot é administrador, publique "
                    "uma nova mensagem e tente novamente."
                )
            )
