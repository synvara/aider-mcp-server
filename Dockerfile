FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install git (required for aider)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy pyproject.toml and lockfile
COPY pyproject.toml uv.lock* ./

# Copy the source code
COPY src/ ./src/
COPY ai_docs/ ./ai_docs/
COPY specs/ ./specs/
COPY .env.sample ./.env.sample
COPY README.md ./

# Install dependencies using uv
RUN uv pip install -e .

# Create a directory for the project that will be mounted
RUN mkdir /project

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the entrypoint
ENTRYPOINT ["aider-mcp-server"]

# Default command (can be overridden)
CMD ["--editor-model", "gemini/gemini-2.5-pro-exp-03-25", "--current-working-dir", "/project"]