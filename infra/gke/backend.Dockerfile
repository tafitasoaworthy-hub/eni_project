FROM python:3.13-slim AS builder
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PSYCOPG_IMPL=python
WORKDIR /app
COPY requirements.txt .
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        build-essential libpq5 libjpeg-dev zlib1g-dev libtiff-dev \
        libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev \
        libharfbuzz-dev libfribidi-dev libxcb1-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --no-binary=Pillow -r requirements.txt gunicorn whitenoise
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

FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PSYCOPG_IMPL=python
WORKDIR /app
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        libpq5 libjpeg62-turbo zlib1g libtiff6 libfreetype6 liblcms2-2 \
        libwebp7 libopenjp2-7 libharfbuzz0b libfribidi0 libxcb1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /app/ /app/
# pip is only needed while building the image. Recent pip versions ship a
# bundled SBOM for vendored tools that must not be included in production.
RUN rm -rf /usr/local/lib/python3.13/site-packages/pip \
    /usr/local/lib/python3.13/site-packages/pip-*.dist-info \
    /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/').read()"
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
