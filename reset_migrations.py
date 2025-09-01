#!/usr/bin/env python
"""
Script para resetar migrações e resolver conflitos de dependências
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def reset_migrations():
    """Reset migrations to resolve dependency conflicts"""
    print("🔄 Resetando migrações...")
    
    # Remover arquivo de banco se existir
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Removido {db_file}")
    
    # Fazer migrações iniciais
    print("📦 Criando migrações iniciais...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("🗄️ Aplicando migrações...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Migrações resetadas com sucesso!")

if __name__ == '__main__':
    reset_migrations()
