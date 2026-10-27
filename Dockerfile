FROM python:3.14.7-slim

# Debian security fixes land between base image releases, and CI's Trivy gate
# fails on fixable HIGH and CRITICAL findings.
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

ARG COMMIT=unknown
ENV COMMIT=$COMMIT \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
# pip goes last: it vendors its own dependencies, and the bot never installs anything.
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt \
 && pip check \
 && pip uninstall -y pip

COPY whisper-consumer.py ./
COPY tests ./tests

USER 1000:1000
# Healthy while connected to Kafka: the bot touches /tmp/healthy every 30 s then.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import os, sys, time; sys.exit(time.time() - os.path.getmtime('/tmp/healthy') > 90)"
# BROKER, TOPIC_NAME and BOT_TOKEN come from the environment.
CMD ["python", "whisper-consumer.py"]
