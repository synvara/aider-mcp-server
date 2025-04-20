# Repository Variables for GitHub Workflows

When using this template, you'll need to set several repository variables and secrets to make the workflows work with your organization. Below is a list of variables you should configure in your repository settings.

## Variables

| Variable Name            | Description                      | Example Value                        | Required                   |
| ------------------------ | -------------------------------- | ------------------------------------ | -------------------------- |
| `DOCKER_USER`            | Docker Hub username              | `your-username`                      | Yes                        |
| `DOCKER_IMAGE_NAME`      | Base name for your Docker images | `your-app-name`                      | No (defaults to repo name) |
| `DOCKER_BUILDX_ENDPOINT` | Your Docker Buildx endpoint      | `your-username/your-buildx-endpoint` | Yes (for cloud builders)   |

## Secrets

| Secret Name            | Description                              | Example Value                                                         | Required               |
| ---------------------- | ---------------------------------------- | --------------------------------------------------------------------- | ---------------------- |
| `DOCKER_PAT`           | Docker Hub Personal Access Token         | `dckr_pat_xxxxxxxxxxxx`                                               | Yes (for Docker)       |
| `APPROVER_APP_ID`      | GitHub App ID for PR approver            | `12345`                                                               | Yes (for auto-approve) |
| `APPROVER_PRIVATE_KEY` | GitHub App private key for PR approver   | `-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----` | Yes (for auto-approve) |
| `VERCEL_TOKEN`         | Vercel API token for preview deployments | `xxxxxxxxxxxxxxx`                                                     | Yes (for preview)      |
| `VERCEL_ORG_ID`        | Vercel organization ID                   | `team_xxxxxxxx`                                                       | Yes (for preview)      |
| `VERCEL_PROJECT_ID`    | Vercel project ID                        | `prj_xxxxxxxx`                                                        | Yes (for preview)      |

## Workflow Customization

### Auto-Approve Trigger Workflow

For the auto-approve workflow, you should update the workflow reference in `.github/workflows/auto-approve-trigger.yml` to point to your organization's reusable workflow:

```yaml
# Change this line:
uses: synvara/synvara-actions/.github/workflows/reusable-pr-approve.yml@main

# To your organization's repository:
uses: your-org/your-actions-repo/.github/workflows/reusable-pr-approve.yml@main
```

### Docker Workflow

The Docker workflow requires:

1. `DOCKER_USER` - Your Docker Hub username
2. `DOCKER_PAT` - Your Docker Hub Personal Access Token
3. `DOCKER_BUILDX_ENDPOINT` - Your Docker Buildx endpoint for cloud builders

If you don't want to use Docker cloud builders, you can modify the `docker.yml` workflow to use the standard Docker Buildx setup:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  # Remove the 'with' section or just the driver and endpoint lines
  # with:
  #   install: true  # You might still want this
```

### GitHub Container Registry

The workflow now uses GitHub's built-in `GITHUB_TOKEN` for authentication to GitHub Container Registry, so no additional secrets are required.

This approach is recommended by GitHub and provides better security by avoiding the use of long-lived personal access tokens. The images are automatically connected to your repository with appropriate metadata through OCI labels.
