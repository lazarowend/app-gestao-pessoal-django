from django.shortcuts import render, redirect
from .models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from .utils import calcula_total
from extrato.models import Valores
from datetime import datetime

def home(request):
    contas = Conta.objects.all()
    valores = Valores.objects.filter(data__month=datetime.now().month)
    saida = Valores.objects.filter(tipo='S')
    entrada = Valores.objects.filter(tipo='E')

    # função para calcular o valor total de todas as contas juntas
    saldo_total = calcula_total(contas, 'valor')
    
    total_entrada = calcula_total(entrada, 'valor')
    total_saida = calcula_total(saida, 'valor')

    context = {
        'total_entrada': total_entrada,
        'total_saida': total_saida,
        'contas': contas,
        'saldo_total': saldo_total,
    }

    return render(request, 'perfil/home.html', context)


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_conta = contas.aggregate(Sum('valor'))

    context = {
        'contas': contas,
        'total_conta': total_conta,
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