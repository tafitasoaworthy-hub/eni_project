FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PSYCOPG_IMPL=python
WORKDIR /app
COPY requirements.txt .
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt gunicorn whitenoise
COPY manage.py ./
COPY config/ ./config/
COPY accounts/ ./accounts/
COPY aiassistant/ ./aiassistant/
COPY api/ ./api/
COPY core/ ./core/
COPY dashboard/ ./dashboard/
COPY documents/ ./documents/
COPY enrollments/ ./enrollments/
COPY schedules/ ./schedules/
COPY templates/ ./templates/
COPY static/ ./static/
RUN DJANGO_SERVE_STATIC=true python manage.py collectstatic --noinput && mkdir -p /app/media
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/').read()"
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
