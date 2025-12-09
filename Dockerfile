# Use uma imagem oficial do Python
FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache de layers)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar projeto
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor a porta (Railway vai definir a porta real)
EXPOSE $PORT

# Comando de startup otimizado
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn argus_ia.wsgi:application --bind 0.0.0.0:$PORT --workers=2 --threads=4 --worker-class=gthread"]