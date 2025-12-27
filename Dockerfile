FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    tor \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY torrc /etc/tor/torrc

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/media /app/staticfiles /var/lib/tor && \
    chown -R appuser:appuser /app /var/lib/tor && \
    chmod 700 /var/lib/tor

COPY --chown=appuser:appuser . .
COPY --chown=appuser:appuser entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

USER appuser

EXPOSE 8000 9050

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
