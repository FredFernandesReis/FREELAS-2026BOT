from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "telegram_id",
        "username",
        "email",
        "administrador",
        "criado_em",
    )

    search_fields = (
        "nome",
        "telegram_id",
        "username",
        "email",
    )

    list_filter = (
        "administrador",
        "aguardando_email",
    )

    ordering = ("-criado_em",)