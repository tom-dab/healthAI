FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer les dossiers de données attendus par les scripts
RUN mkdir -p data/raw data/clean_bdd data/clean_ml rapport logs

# Lancer le pipeline depuis le dossier pipelines/
# Le WORKDIR est /app, donc les imports entre fichiers du même dossier fonctionnent
CMD ["sh", "-c", "cd /app/pipelines && python run_pipeline.py"]
