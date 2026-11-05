
from django.contrib import admin
from .models import Assinatura, Pagamento


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "administrador",
        "valor",
        "status",
        "inicio",
        "vencimento",
        "criado_em",
    )

    search_fields = (
        "cliente__nome",
        "cliente__telegram_id",
        "cliente__email",
        "cakto_subscription_id",
    )

    list_filter = (
        "status",
        "administrador",
    )

    ordering = ("-criado_em",)


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assinatura",
        "valor",
        "status",
        "metodo",
        "cakto_order_id",
        "criado_em",
    )

    search_fields = (
        "assinatura__cliente__nome",
        "assinatura__cliente__telegram_id",
        "cakto_order_id",
        "cakto_event_id",
    )

    list_filter = (
        "status",
        "metodo",
    )

    ordering = ("-criado_em",)
