"""Módulo models/parametrizacao."""
from __future__ import annotations
from typing import Any
from django.db import models
from .base import BaseModel

class Parametrizacao(BaseModel):
    """Model para gerenciar parâmetros de cálculo de habilitados."""
    porcentagem_pcd = models.FloatField(default=0.05, verbose_name='Porcentagem PCD', help_text='Porcentagem padrão para cálculo de habilitados PCD (padrão: 0.05 = 5%)')
    porcentagem_nna = models.FloatField(default=0.2, verbose_name='Porcentagem NNA', help_text='Porcentagem padrão para cálculo de habilitados NNA (padrão: 0.20 = 20%)')

    class Meta:
        """Define Meta."""
        verbose_name = 'Parametrização'
        verbose_name_plural = 'Parametrizações'
        ordering = ['-criado_em']

    def __str__(self) -> Any:
        """Executa   str  .
        
        Args:
            self: Instância do objeto.
        
        Returns:
            Resultado da operação.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        return f'Parametrização - PCD: {self.porcentagem_pcd}, NNA: {self.porcentagem_nna}'
