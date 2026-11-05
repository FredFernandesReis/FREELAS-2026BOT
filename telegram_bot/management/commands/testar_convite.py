
from django.core.management.base import BaseCommand
from telegram_bot.services import criar_link_convite


class Command(BaseCommand):
    help = "Testa a criação de um convite individual"

    def handle(self, *args, **options):
        try:
            link = criar_link_convite()

            self.stdout.write(
                self.style.SUCCESS(
                    "Convite criado com sucesso!"
                )
            )

            self.stdout.write(link)

        except Exception as erro:
            self.stderr.write(
                self.style.ERROR(f"Erro: {erro}")
            )
