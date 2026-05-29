"""
Django management command to clear all candidatos.
"""

from django.core.management.base import BaseCommand

from candidatos.models import Candidato


class Command(BaseCommand):
    help = "Remove todos os registros da tabela de candidatos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirma a exclusão de todos os candidatos",
        )

    def handle(self, *args, **options):
        confirm = options["confirm"]

        # Contar registros existentes
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
            # Método 1: Usando delete() em queryset (mais seguro)
            Candidato.objects.all().delete()

            # Método 2: Usando SQL direto (mais rápido, mas menos seguro)
            # with connection.cursor() as cursor:
            #     cursor.execute("DELETE FROM candidatos_candidato")

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {total_registros} candidatos removidos com sucesso!"
                )
            )

            # Verificar se realmente foi limpo
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
