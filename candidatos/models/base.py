"""Módulo models/base."""
import uuid

from django.db import models


class BaseModel(models.Model):
    """Base model with common fields for all models."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização"
    )
    esta_ativo = models.BooleanField(default=True, verbose_name="Está Ativo?")

    class Meta:
        """Define Meta."""
        abstract = True
