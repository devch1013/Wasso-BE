FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false
RUN python -m pip install --no-cache-dir poetry
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Install project
RUN poetry install --no-interaction --no-ansi

# Collect static files
ENV DJANGO_SETTINGS_MODULE=config.django.base \
    PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "config.wsgi:application"]