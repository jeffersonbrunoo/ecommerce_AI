# 1. Imagem base
FROM python:3.10-slim

# 2. Definir diretório de trabalho
WORKDIR /app

# 3. Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar o código da aplicação
COPY . .

# 5. Expôr a porta do Flask
EXPOSE 5000

# 6. Variável de ambiente para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 7. Comando de inicialização
CMD ["flask", "run"]
