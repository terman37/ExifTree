# Use the official python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install exiftool AND cron system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    exiftool \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency configuration files
COPY pyproject.toml uv.lock README.md ./

# Install project dependencies
RUN uv sync --frozen --no-install-project

# Copy source code and config folder
COPY src/ ./src
COPY config/ ./config

# Sync the project itself
RUN uv sync --frozen

# defaults to every 5 minutes
ARG CRON_SCHEDULE="*/5 * * * *"

# Create the cron job directly inside the Dockerfile
# Redirect output directly to /proc/1/fd/1 (Docker's stdout) and /proc/1/fd/2 (Docker's stderr)
RUN echo "${CRON_SCHEDULE} . /etc/environment; cd /app && uv run --project /app python -m exiftree.main > /proc/1/fd/1 2> /proc/1/fd/2\n" > /etc/cron.d/exiftree-cron \
    && chmod 0644 /etc/cron.d/exiftree-cron \
    && crontab /etc/cron.d/exiftree-cron

# Show env vars (like EXIFTREE_CONFIG_FILE) then run cron in the foreground.
CMD ["/bin/sh", "-c", "printenv | grep -v 'no_proxy' > /etc/environment && exec cron -f"]
