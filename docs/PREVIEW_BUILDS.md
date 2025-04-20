# Preview Builds Guide

This document explains how to work with preview builds in the aider-mcp-server project.

## Overview

Preview builds are automatically created when you open or update a pull request targeting the `main` branch. These builds allow reviewers to test changes before merging, without needing to build the Docker image locally.

## How Preview Builds Work

1. When a pull request is created or updated, the GitHub Actions workflow creates a new Docker image
2. The image is pushed to GitHub Container Registry (GHCR) with two tags:
   - `ghcr.io/synvara/aider-mcp-server:preview-pr-{PR_NUMBER}`
   - `ghcr.io/synvara/aider-mcp-server:preview-sha-{COMMIT_SHA}`
3. A comment is automatically added to the PR with instructions for pulling and running the image

## Using Preview Builds

### Pull the Preview Image

```bash
# Replace {PR_NUMBER} with the actual PR number
docker pull ghcr.io/synvara/aider-mcp-server:preview-pr-{PR_NUMBER}

# Alternatively, you can use the commit SHA tag (more precise)
docker pull ghcr.io/synvara/aider-mcp-server:preview-sha-{COMMIT_SHA}
```

### Run the Preview Image

```bash
# Run the container with your project mounted as a volume
docker run -v /path/to/your/project:/workspace \
  -e GEMINI_API_KEY=your_gemini_api_key_here \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e ANTHROPIC_API_KEY=your_anthropic_api_key_here \
  -p 8000:8000 \
  ghcr.io/synvara/aider-mcp-server:preview-pr-{PR_NUMBER} \
  --editor-model "gpt-4o" \
  --current-working-dir "/workspace"
```

### Setting Up Claude Code with a Preview Build

```bash
claude mcp add aider-mcp-server-preview -s local \
  -- \
  docker run -v /path/to/your/project:/workspace \
  -e GEMINI_API_KEY=your_gemini_api_key_here \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e ANTHROPIC_API_KEY=your_anthropic_api_key_here \
  ghcr.io/synvara/aider-mcp-server:preview-pr-{PR_NUMBER} \
  --editor-model "gemini/gemini-2.5-pro-exp-03-25" \
  --current-working-dir "/workspace"
```

## Troubleshooting

### Image Not Found

If you encounter an error like `Error response from daemon: manifest for ghcr.io/synvara/aider-mcp-server:preview-pr-X not found`, check the following:

1. Verify that the pull request is still open (preview images may be cleaned up after a PR is closed)
2. Check that the PR number is correct
3. Ensure that the GitHub Actions workflow completed successfully
4. Check the GitHub Actions logs for any errors in the build process

### Authentication Issues

If you're having trouble pulling the image due to authentication issues:

```bash
# Log in to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Preview Workflow Not Triggered

The preview workflow only runs when specific files are changed in the pull request. If you don't see a preview build, check if the PR included changes to:

- `Dockerfile`
- `.dockerignore`
- `pyproject.toml`
- `src/**`
- `.github/workflows/preview.yml`

## Best Practices

1. Always test the preview build before merging a PR
2. Include instructions in your PR description for reviewers on how to test the changes
3. If your PR affects the Docker image, verify that the preview image builds and runs correctly
