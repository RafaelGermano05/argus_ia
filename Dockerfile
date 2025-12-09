FROM python:3.10-slim

# Instalar dependências do sistema para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Coletar static files ANTES de rodar
RUN python manage.py collectstatic --noinput

# Não exponha porta fixa - Railway usa $PORT
CMD ["gunicorn", "argus_ia.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
