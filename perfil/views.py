from django.shortcuts import render, redirect
from .models import Conta, Categoria
from contas.models import ContaPagar
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from .utils import calcula_total, qtd_contas,  calcula_equilibrio_financeiro
from extrato.models import Valores
from datetime import datetime

def home(request):
    contas = Conta.objects.all()
    valores = Valores.objects.filter(data__month=datetime.now().month)
    saida = Valores.objects.filter(tipo='S')
    entrada = Valores.objects.filter(tipo='E')

    quantidade_contas = qtd_contas()
    contas_vencidas = quantidade_contas['contas_vencidas']
    contas_proximas_vencimento = quantidade_contas['contas_proximas_vencimento']

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    # função para calcular o valor total de todas as contas juntas
    saldo_total = calcula_total(contas, 'valor')
    
    total_entrada = calcula_total(entrada, 'valor')
    total_saida = calcula_total(saida, 'valor')

    contas_a_pagar_do_mes = ContaPagar.objects.all()
    contas_a_pagar_do_mes = calcula_total(contas_a_pagar_do_mes, 'valor')
    entrada_do_mes = Valores.objects.filter(tipo='E', data__month=datetime.now().month).aggregate(total=Sum('valor'))['total']

    total_livre = float(entrada_do_mes - contas_a_pagar_do_mes)

    context = {
        'total_entrada': total_entrada,
        'total_saida': total_saida,
        'contas': contas,
        'saldo_total': saldo_total,
        'contas_vencidas': contas_vencidas,
        'contas_proximas_vencimento': contas_proximas_vencimento,
        'percentual_gastos_essenciais': percentual_gastos_essenciais,
        'percentual_gastos_nao_essenciais': percentual_gastos_nao_essenciais,
        'saldo_total': saldo_total,
        'entrada_do_mes': entrada_do_mes,
        'contas_a_pagar_do_mes': contas_a_pagar_do_mes,
        'total_livre': total_livre
    }

    return render(request, 'perfil/home.html', context)


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    saldo_total = calcula_total(contas, 'valor')

    context = {
        'contas': contas,
        'saldo_total': saldo_total,
        'categorias': categorias
    }

    return render(request, 'perfil/gerenciar.html', context)


def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    # strip() vai retirar os espaçoes para validação do apelido
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    

    conta = Conta(
        apelido = apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    
    conta = Conta.objects.get(id=id)

    conta.delete()
    messages.add_message(request, constants.WARNING, 'Conta deletada com sucesso!')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')

    return redirect('/perfil/gerenciar/')


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria atualizado com sucesso!')
    return redirect('/perfil/gerenciar/')