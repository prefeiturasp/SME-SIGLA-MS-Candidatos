"""Django management command to clear all candidatos."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from candidatos.models import Candidato


class Command(BaseCommand):
    """Representa Command."""

    help = "Remove todos os registros da tabela de candidatos"

    def add_arguments(self, parser: Any) -> None:
        """Registra os argumentos da linha de comando."""
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirma a exclusão de todos os candidatos",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Roda a lógica principal do comando."""
        confirm = options["confirm"]
        total_registros = Candidato.objects.count()
        if total_registros == 0:
            self.stdout.write(
                self.style.WARNING("⚠️  Não há candidatos para remover.")
            )
            return
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Você está prestes a remover {total_registros} candidatos!"  # noqa: E501
                )
            )
            self.stdout.write("Use --confirm para confirmar a operação.")
            return
        self.stdout.write(
            self.style.SUCCESS(f"Removendo {total_registros} candidatos...")
        )
        try:
            Candidato.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {total_registros} candidatos removidos com sucesso!"
                )
            )
            registros_restantes = Candidato.objects.count()
            if registros_restantes == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ Tabela completamente limpa!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Ainda restam {registros_restantes} candidatos."
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao remover candidatos: {e}")
            )
