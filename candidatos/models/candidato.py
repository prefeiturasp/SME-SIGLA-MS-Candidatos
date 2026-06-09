"""Módulo models/candidato."""
from __future__ import annotations
from typing import Any
from datetime import date
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from .base import BaseModel

class Candidato(BaseModel):
    """Model for managing candidates."""
    STATUS_CHOICES = [('ativo', 'Ativo'), ('inativo', 'Inativo'), ('suspenso', 'Suspenso')]
    GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro'), ('N', 'Prefiro não informar')]
    nome = models.CharField(max_length=200, verbose_name='Nome')
    cpf = models.CharField(max_length=14, verbose_name='CPF')
    email = models.EmailField(max_length=254, verbose_name='Email')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    celular = models.CharField(max_length=20, blank=True, verbose_name='Celular')
    rg = models.CharField(max_length=20, blank=True, verbose_name='RG')
    registro_funcional = models.CharField(max_length=50, blank=True, verbose_name='Registro Funcional')
    vinculo = models.CharField(max_length=100, blank=True, verbose_name='Vínculo')
    data_nascimento = models.DateField(default=date.today)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, verbose_name='Gênero')
    endereco = models.TextField(blank=True, verbose_name='Endereço')
    numero = models.CharField(max_length=20, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=120, blank=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    estado = models.CharField(max_length=2, blank=True, verbose_name='Estado')
    cep = models.CharField(max_length=9, blank=True, verbose_name='CEP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name='Status')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    history = AuditlogHistoryField()

    class Meta:
        """Define Meta."""
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'
        ordering = ['nome']

    def __str__(self) -> Any:
        """Executa   str  .
        
        Args:
            self: Instância do objeto.
        
        Returns:
            Resultado da operação.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        return self.nome
auditlog.register(Candidato)
