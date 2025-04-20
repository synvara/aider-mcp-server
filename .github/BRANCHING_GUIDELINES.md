# Branching Guidelines

This document defines the branching strategy and naming conventions for the Agentic GitHub repository.

## Branch Structure

The repository follows a structured branching model:

- **`main`**: The primary branch containing production-ready code. All releases are made from this branch.
- **`develop`**: The integration branch where feature development is combined. This is the base branch for all feature development.
- **Feature branches**: Short-lived branches created for specific features, bug fixes, or other changes.

## Branch Flow

1. Development work is done in feature branches created from `develop`.
2. When a feature is complete, it is merged back into `develop` via a pull request.
3. When `develop` is stable and ready for release, it is merged into `main`.
4. Hotfixes for production issues can be branched directly from `main` and merged back into both `main` and `develop`.

## Branch Naming Convention

All branches must follow this naming convention:

```
^(main|develop|staging|(feature|bugfix|hotfix|release|test|docs|refactor|chore)/([A-Za-z]+-[0-9]+)/([a-z0-9-.]+))
```

### Explanation:

1. **Standard Branches**:
   - `main`: Main production branch
   - `develop`: Integration branch for development
   - `staging`: Pre-production testing branch (if needed)

2. **Feature Branches**:
   - Format: `<type>/<issue-reference>/<short-description>`
   
3. **Branch Types**:
   - `feature/`: New features or significant enhancements
   - `bugfix/`: Fixes for bugs that are not critical production issues
   - `hotfix/`: Urgent fixes for production issues
   - `release/`: Release preparation branches
   - `test/`: Experimental branches for testing concepts
   - `docs/`: Documentation-only changes
   - `refactor/`: Code refactoring without behavior changes
   - `chore/`: Maintenance tasks, dependency updates, etc.
   
4. **Issue Reference**:
   - Format: `<project-code>-<issue-number>`
   - Example: `E1S3` (Epic 1, Story 3) or `BUG-42` (Bug issue #42)
   
5. **Description**:
   - Brief description of the branch content
   - Use lowercase letters, numbers, hyphens, and periods only
   - Be descriptive but concise

### Examples:

✅ **Valid branch names**:
- `feature/E1S3/setup-project-repository`
- `bugfix/BUG-42/fix-authentication-issue`
- `docs/DOC-7/update-readme`
- `hotfix/PROD-15/fix-critical-security-issue`
- `refactor/TECH-31/simplify-database-queries`

❌ **Invalid branch names**:
- `feature-project-setup` (missing issue reference and proper format)
- `feature/setup_project` (missing issue reference and using underscore)
- `TECH-31/database-refactor` (missing branch type)
- `feature/TECH-31/Refactor-Database` (using uppercase in description)

## Working with Branches

### Creating a New Branch

```bash
# Make sure you're on the develop branch
git checkout develop

# Pull the latest changes
git pull

# Create a new feature branch
git checkout -b feature/E1S3/setup-project-repository
```

### Keeping Your Branch Updated

```bash
# Get the latest changes from develop
git checkout develop
git pull

# Switch back to your feature branch
git checkout feature/E1S3/setup-project-repository

# Merge the latest changes from develop
git merge develop

# Resolve any conflicts and commit
```

### Completing a Branch

1. Push your branch to GitHub
2. Create a pull request to merge into `develop`
3. Address any review comments
4. Once approved, merge the pull request

## Branch Protection

The `main` and `develop` branches are protected:

- Direct pushes to these branches are not allowed
- Changes must go through pull requests
- Pull requests require at least one approval
- Status checks must pass before merging

## Best Practices

1. **Keep branches focused**:
   - Each branch should address a single feature, bug fix, or task
   - Avoid mixing unrelated changes in a single branch

2. **Keep branches short-lived**:
   - Complete work quickly to avoid long-running branches
   - Merge feature branches into `develop` as soon as they are completed

3. **Commit regularly**:
   - Make small, focused commits with clear messages
   - Push changes to the remote branch regularly

4. **Update branches frequently**:
   - Regularly merge changes from `develop` into your feature branch
   - Resolve conflicts promptly

By following these guidelines, we maintain a clean repository history and ensure smooth collaboration.
