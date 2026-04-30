FROM python:3.11-slim
 
WORKDIR /app
 
# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
 
# Copier et installer les dépendances Python EN PREMIER
# → ce layer est caché tant que requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copier le code source
COPY . .
 
EXPOSE 8000
 
# PRODUCTION : pas de --reload (consomme des ressources inutilement)
# Pour le dev avec hot-reload, surcharger dans docker-compose via
# command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]