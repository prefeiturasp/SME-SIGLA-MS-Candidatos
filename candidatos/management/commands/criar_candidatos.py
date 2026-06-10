"""Django management command to create sample candidatos."""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

from django.core.management.base import BaseCommand

from candidatos.models import Candidato


class Command(BaseCommand):
    """Define Command."""

    help = "Cria candidatos de exemplo para desenvolvimento"

    def add_arguments(self, parser: Any) -> None:
        """Registra argumentos da linha de comando.

        Args:
            parser: Parser de argumentos do Django management.

        Returns:
            Nenhum valor; registra opções de linha de comando.
        """
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Número de candidatos a serem criados (padrão: 10)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Cria candidatos de exemplo para desenvolvimento e testes.

        Args:
            *args: Argumentos posicionais do comando.
            **options: Opções parseadas, incluindo ``count``.

        Returns:
            Nenhum valor; exibe progresso e estatísticas no stdout.
        """
        count = options["count"]
        self.stdout.write(self.style.SUCCESS(f"Criando {count} candidatos..."))
        nomes = [
            "João Silva",
            "Maria Santos",
            "Pedro Oliveira",
            "Ana Costa",
            "Carlos Pereira",
            "Lucia Ferreira",
            "Roberto Alves",
            "Fernanda Lima",
            "Marcos Souza",
            "Juliana Rocha",
            "Rafael Mendes",
            "Camila Dias",
            "Diego Rodrigues",
            "Patricia Nunes",
            "Thiago Barbosa",
            "Larissa Gomes",
            "Felipe Castro",
            "Beatriz Moreira",
            "Gabriel Martins",
            "Isabela Ramos",
        ]
        cidades_estados = [
            ("São Paulo", "SP"),
            ("Rio de Janeiro", "RJ"),
            ("Belo Horizonte", "MG"),
            ("Salvador", "BA"),
            ("Brasília", "DF"),
            ("Fortaleza", "CE"),
            ("Manaus", "AM"),
            ("Curitiba", "PR"),
            ("Recife", "PE"),
            ("Porto Alegre", "RS"),
        ]
        status_choices = ["ativo", "inativo", "suspenso"]
        genero_choices = ["M", "F", "O", "N"]
        candidatos_criados = []
        for i in range(count):
            cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            while Candidato.objects.filter(cpf=cpf).exists():
                cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            nome_base = nomes[i % len(nomes)].lower().replace(" ", ".")
            email = f"{nome_base}{i + 1}@email.com"
            while Candidato.objects.filter(email=email).exists():
                email = f"{nome_base}{i + 1}{random.randint(1, 999)}@email.com"
            hoje = date.today()
            idade_min = 18
            idade_max = 65
            anos_aleatorios = random.randint(idade_min, idade_max)
            data_nascimento = hoje - timedelta(days=anos_aleatorios * 365)
            cidade, estado = random.choice(cidades_estados)
            candidato = Candidato.objects.create(
                nome=nomes[i % len(nomes)],
                cpf=cpf,
                email=email,
                telefone=f"({random.randint(11, 99)}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}",
                data_nascimento=data_nascimento,
                genero=random.choice(genero_choices),
                endereco=f'Rua {random.choice(['das Flores', 'Augusta', 'Paulista', 'Copacabana'])}, {random.randint(100, 999)}',
                cidade=cidade,
                estado=estado,
                cep=f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                status=random.choice(status_choices),
                observacoes=f"Candidato de exemplo {i + 1}",
            )
            self.stdout.write(
                f"  ✓ Criado candidato: {candidato.nome} ({candidato.cidade}/{candidato.estado})"
            )
            candidatos_criados.append(candidato)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ {len(candidatos_criados)} candidatos criados com sucesso!"
            )
        )
        ativos = Candidato.objects.filter(status="ativo").count()
        inativos = Candidato.objects.filter(status="inativo").count()
        suspensos = Candidato.objects.filter(status="suspenso").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"📊 Estatísticas: {ativos} ativos, {inativos} inativos, {suspensos} suspensos"
            )
        )
