
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependencias para ngrok
RUN apt-get update && \
    apt-get install -y curl unzip && \
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && \
    apt-get install -y ngrok

# Expone el puerto de la API
EXPOSE 5060
