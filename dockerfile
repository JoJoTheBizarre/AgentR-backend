# Use Python 3.12 slim base image
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.2.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN poetry self add poetry-plugin-export

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Generate requirements.txt including PostgreSQL driver
# First add psycopg2-binary temporarily (won't modify host pyproject.toml)
RUN poetry add psycopg2-binary --no-interaction
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Second stage for runtime
FROM python:3.12-slim AS runtime

# Install runtime system dependencies (PostgreSQL client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy requirements.txt from builder stage
COPY --from=builder /app/requirements.txt .

# Upgrade pip and install dependencies as root
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Switch to non-root user
USER appuser
WORKDIR /home/appuser/app

# Copy application source code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser main.py ./

# Set environment variables
ENV PYTHONPATH=/home/appuser/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/appuser/.local/bin:$PATH"

# Expose FastAPI port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]