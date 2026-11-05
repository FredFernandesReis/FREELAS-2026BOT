
from django.urls import path
from . import views

urlpatterns = [
    path(
        "cakto/",
        views.receber_webhook,
        name="receber_webhook"
    ),
]
