
from django.db import models
from django.utils import timezone

from clientes.models import Cliente


class Assinatura(models.Model):

    STATUS = [
        ("PENDENTE", "Pendente"),
        ("ATIVA", "Ativa"),
        ("CANCELADA", "Cancelada"),
        ("EXPIRADA", "Expirada"),
        ("REEMBOLSADA", "Reembolsada"),
        ("CHARGEBACK", "Chargeback"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="assinaturas"
    )

    administrador = models.CharField(
        max_length=1,
        blank=True,
        default=""
    )

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=14.99
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default="PENDENTE"
    )

    inicio = models.DateTimeField(
        null=True,
        blank=True
    )

    vencimento = models.DateTimeField(
        null=True,
        blank=True
    )

    cakto_subscription_id = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def esta_ativa(self):
        return (
            self.status == "ATIVA"
            and self.vencimento is not None
            and self.vencimento > timezone.now()
        )

    def __str__(self):
        return f"{self.cliente} - {self.status}"


class Pagamento(models.Model):

    STATUS = [
        ("PENDENTE", "Pendente"),
        ("APROVADO", "Aprovado"),
        ("RECUSADO", "Recusado"),
        ("REEMBOLSADO", "Reembolsado"),
        ("CHARGEBACK", "Chargeback"),
    ]

    assinatura = models.ForeignKey(
        Assinatura,
        on_delete=models.PROTECT,
        related_name="pagamentos"
    )

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=14.99
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default="PENDENTE"
    )

    cakto_order_id = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    cakto_event_id = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    metodo = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pagamento {self.id} - {self.status}"
