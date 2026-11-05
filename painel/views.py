
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from clientes.models import Cliente
from assinaturas.models import Assinatura, Pagamento


@login_required(login_url="/admin/login/")
def dashboard(request):

    total_clientes = Cliente.objects.count()

    total_assinaturas = Assinatura.objects.count()

    assinaturas_ativas = Assinatura.objects.filter(
        status="ATIVA"
    ).count()

    assinaturas_pendentes = Assinatura.objects.filter(
        status="PENDENTE"
    ).count()

    total_pagamentos = Pagamento.objects.count()

    pagamentos_aprovados = Pagamento.objects.filter(
        status="APROVADO"
    ).count()

    ultimos_clientes = Cliente.objects.order_by(
        "-criado_em"
    )[:10]

    ultimas_assinaturas = Assinatura.objects.select_related(
        "cliente"
    ).order_by("-criado_em")[:10]

    ultimos_pagamentos = Pagamento.objects.select_related(
        "assinatura",
        "assinatura__cliente"
    ).order_by("-criado_em")[:10]

    contexto = {
        "total_clientes": total_clientes,
        "total_assinaturas": total_assinaturas,
        "assinaturas_ativas": assinaturas_ativas,
        "assinaturas_pendentes": assinaturas_pendentes,
        "total_pagamentos": total_pagamentos,
        "pagamentos_aprovados": pagamentos_aprovados,
        "ultimos_clientes": ultimos_clientes,
        "ultimas_assinaturas": ultimas_assinaturas,
        "ultimos_pagamentos": ultimos_pagamentos,
    }

    return render(request, "painel/dashboard.html", contexto)
