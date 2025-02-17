# Basierend auf einem Python-Image
FROM python

# Arbeitsverzeichnis für die nachfolgenden Befehle festlegen
WORKDIR /app

# Anwendung in das Image kopieren
COPY . /app

# Abhängigkeiten installieren
RUN pip install -r requirements.txt

# Befehl, der beim Start jedes Containers ausgeführt wird
CMD ["python", "app.py"]
