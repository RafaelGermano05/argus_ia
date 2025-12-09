# Use imagem oficial do Python
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Configurações
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar projeto
COPY . .

# Coletar estáticos
RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8000

# O Railway vai sobrescrever esse CMD com o startCommand
CMD ["gunicorn", "argus_ia.wsgi:application", "--bind", "0.0.0.0:8000"]
