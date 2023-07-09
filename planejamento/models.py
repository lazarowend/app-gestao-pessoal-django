from django.db import models
from datetime import datetime
from django.db.models import Sum

# Create your models here.
class Categoria(models.Model):
    categoria = models.CharField(max_length=50)
    essencial = models.BooleanField(default=False)
    valor_planejamento = models.FloatField(default=0)

    def __str__(self):
        return self.categoria
    
    def total_gasto(self):
        from extrato.models import Valores
        valores = Valores.objects.filter(categoria__id = self.id).filter(data__month=datetime.now().month).aggregate(Sum('valor'))
        return valores['valor__sum'] if valores['valor__sum'] else 0

    def calcula_percentual_gasto_por_categoria(self):
        # o try para evitar o ZeroDivisionError (Erro de divisão por zero)
        try:
            return (self.total_gasto() * 100) / self.valor_planejamento
        except:
            return 0