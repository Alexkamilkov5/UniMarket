# ---------- builder stage ----------
FROM python:3.11-slim AS builder

# system deps for some Python packages (bcrypt, psycopg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  libpq-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

# create working dir
WORKDIR /app

# copy only requirements first (cache layer)
COPY requirements.txt requirements-dev.txt ./

# create an isolated venv inside image (optional but nice)
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# install dependencies into venv
RUN pip install --upgrade pip wheel setuptools \
  && pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# run optional build steps (alembic, collect static, type stub generation) here if needed
# RUN alembic upgrade head   <-- usually not during image build for dev

# ---------- final stage ----------
FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# non-root user
RUN useradd --create-home appuser
WORKDIR /app

# copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# copy app files
COPY --from=builder /app /app

# create logs dir
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# switch to non-root user
USER appuser

# expose port 80 inside container
EXPOSE 80

# make start script executable
RUN chmod +x /app/scripts/start.sh

# healthcheck (basic)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/health || exit 1

# default command
CMD ["/app/scripts/start.sh"]

