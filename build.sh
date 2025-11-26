#!/bin/bash

echo "🚀 Iniciando build do ARGUS IA..."

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Aplicar migrações
python manage.py migrate --noinput

echo "✅ Build concluído!"