
from django.db import models


class WebhookEvento(models.Model):

    evento = models.CharField(max_length=100)

    pedido_id = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    identificador = models.CharField(
        max_length=64,
        unique=True
    )

    payload = models.TextField()

    processado = models.BooleanField(default=False)

    recebido_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evento} - {self.pedido_id}"
