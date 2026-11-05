
from django.contrib import admin
from .models import WebhookEvento


@admin.register(WebhookEvento)
class WebhookEventoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "evento",
        "pedido_id",
        "processado",
        "recebido_em",
    )

    list_filter = (
        "evento",
        "processado",
    )

    search_fields = (
        "pedido_id",
        "identificador",
    )

    readonly_fields = (
        "evento",
        "pedido_id",
        "identificador",
        "payload",
        "recebido_em",
    )
