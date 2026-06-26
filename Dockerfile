# Use the official python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install exiftool system dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
    exiftool \
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

# Set entrypoint to run the exiftree script
ENTRYPOINT ["uv", "run", "python", "-m", "exiftree.main"]
