FROM python:3.12.16-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337 AS base
RUN apt-get update \
    && apt-get install --only-upgrade --no-install-recommends -y apt=2.6.2 libapt-pkg6.0=2.6.2 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS secret-bootstrap
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY scripts/prepare-secrets.py /prepare-secrets.py
USER 0:0
CMD ["python", "/prepare-secrets.py"]

FROM base AS application
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONPATH=/app/src
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

FROM application AS runtime
# The standalone API never installs packages; remove the package manager itself.
RUN python -m pip uninstall --yes pip
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "kryptroom_control.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-proxy-headers"]

FROM application AS test
USER root
COPY requirements-dev.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements-dev.lock
COPY tests ./tests
COPY scripts ./scripts
COPY pyproject.toml ./
USER 10001:10001
CMD ["python", "-m", "pytest", "-v", "-m", "postgres", "-o", "cache_dir=/tmp/pytest-cache"]
