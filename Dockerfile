FROM python:3.12-slim

# Define diretório de trabalho
WORKDIR /app

# Fuso operacional usado pelo cron e pelos nomes dos backups
ENV TZ=America/Sao_Paulo

# Instala dependências do sistema
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cron \
    gcc \
    postgresql-client \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primeiro (cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Instala a agenda e protege os executáveis e o log do backup
RUN chmod 0755 scripts/backup_database.sh scripts/docker-entrypoint.sh \
    && install -m 0644 deploy/jaci-backup.cron /etc/cron.d/jaci-backup \
    && touch /var/log/backup.log \
    && chmod 0600 /var/log/backup.log

# Expõe a porta
EXPOSE 8000

# O entrypoint inicia o cron somente para o processo servidor
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Comando para iniciar
CMD ["python", "run.py", "--port", "8000", "--no-restart"]
