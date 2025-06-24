FROM python:3.11-slim

# Instala dependências de sistema necessárias (por exemplo: psycopg2, build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Define o PATH para poetry instalado no user
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copia apenas os arquivos do poetry para otimizar cache
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto (incluindo dev-deps para testes)
RUN poetry install --no-root --with dev

# Copia todo o código do projeto
COPY . .

# Define variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1

# Comando padrão - pode ser sobrescrito pelo docker-compose
CMD ["poetry", "run", "python", "-m", "jenkins_log.controller.jenkins_logs"]
