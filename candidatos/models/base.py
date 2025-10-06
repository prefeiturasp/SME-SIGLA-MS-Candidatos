from django.db import models


class BaseModel(models.Model):
    """
    Base model with common fields for all models
    """
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    esta_ativo = models.BooleanField(default=True)

    class Meta:
        abstract = True
