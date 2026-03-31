FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy source
COPY lumina_geo/ lumina_geo/
COPY api/ api/
COPY static/ static/
COPY cli.py .

# Reports are written here — mount a volume to persist them
RUN mkdir -p /app/reports

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
