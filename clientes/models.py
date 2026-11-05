from django.db import models


class Cliente(models.Model):

    ADMINISTRADORES = [
        ("F", "Freelancer F"),
        ("W", "Freelancer W"),
        ("L", "Freelancer L"),
        ("G", "Freelancer G"),
    ]

    telegram_id = models.BigIntegerField(unique=True)

    username = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    
    email = models.EmailField(
        blank=True,
        default=""
    )

    aguardando_email = models.BooleanField(
        default=False
    )


    nome = models.CharField(
        max_length=150,
        blank=True
    )

    administrador = models.CharField(
        max_length=1,
        choices=ADMINISTRADORES,
        blank=True,
        default=""
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.administrador}"