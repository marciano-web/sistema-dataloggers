FROM python:3.9-slim

WORKDIR /app

# Copiar requirements primeiro para cache do Docker
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório do banco se não existir
RUN mkdir -p src/database

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "src/main.py"]

