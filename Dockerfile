FROM python:3.12-slim

# Install git (required for aider) and other dependencies
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /build

# Copy the source code
COPY . /build/

# Install the package with pip
# This properly creates the aider-mcp-server executable
RUN pip install -e .

# Create project directory for mounting
RUN mkdir /project && mkdir -p /app/logs && chmod 777 /app/logs

# Configure Git to trust the mounted directory
RUN git config --global --add safe.directory /project

# Set environment variables
ENV PYTHONUNBUFFERED=1

# The entrypoint uses the executable created during installation
ENTRYPOINT ["aider-mcp-server"]