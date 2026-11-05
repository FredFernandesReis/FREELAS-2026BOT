from django.http import JsonResponse


def inicio(request):
    return JsonResponse({
        "sistema": "Freelancer BH Região",
        "status": "online",
        "mensagem": "Sistema iniciado com sucesso!"
    })