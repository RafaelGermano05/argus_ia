# Use uma imagem oficial do Python
FROM python:3.10-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie os arquivos de requirements e instale as dependências
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copie todo o projeto para dentro do container
COPY . .

# Coletar arquivos estáticos (importante para Django)
RUN python manage.py collectstatic --noinput

# Exponha a porta que o Django vai rodar
EXPOSE 8000

# Comando para rodar o servidor Django com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "argus_ia.wsgi:application"]