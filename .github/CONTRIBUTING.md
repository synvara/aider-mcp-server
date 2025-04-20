# Contributing to Agentic Development Workflow

Thank you for your interest in contributing to the Agentic Development Workflow project! This document outlines the process and guidelines for contributing.

## Code of Conduct

By participating in this project, you agree to maintain professional and respectful communication with all contributors.

## Getting Started

1. **Fork the repository** and create your branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name develop
   ```

2. **Follow the branch naming convention**:
   - `main` - Production-ready code
   - `develop` - Development integration branch
   - `feature/{issue-id}/{description}` - For new features
   - `bugfix/{issue-id}/{description}` - For bug fixes
   - `hotfix/{issue-id}/{description}` - For urgent fixes to production
   - `release/{version}` - For release preparation
   - `test/{description}` - For experimental tests
   - `docs/{description}` - For documentation updates
   - `refactor/{description}` - For code refactoring
   - `chore/{description}` - For routine tasks and maintenance

3. **Install development dependencies**:
   ```bash
   # Using Poetry
   poetry install --with dev
   # Or using pip
   pip install -e ".[dev]"
   ```

4. **Run tests locally** before committing:
   ```bash
   pytest
   ```

## Development Workflow

1. **Create an issue** for the feature or bug you're working on.
2. **Create a branch** following the naming convention.
3. **Write your code** and corresponding tests.
4. **Ensure all tests pass** and linting checks succeed.
5. **Submit a pull request** to the `develop` branch.

## Pull Request Process

1. Update the README.md or documentation with details of changes, if applicable.
2. Update the CHANGELOG.md following the format.
3. Ensure your PR passes all CI checks.
4. Request review from a maintainer.
5. Your PR will be merged once approved.

## Testing

- Write tests for all new features and bug fixes.
- Maintain or improve test coverage.
- Test both happy paths and edge cases.

## Coding Standards

- Follow PEP 8 style guide for Python code.
- Use meaningful variable and function names.
- Add comments for complex logic.
- Keep functions focused and small.
- Use type hints where appropriate.

## Commit Messages

Follow the conventional commits format:
```
type(scope): short description

Longer description if needed.

Fixes #issue-number
```

Types include: feat, fix, docs, style, refactor, test, chore

## Documentation

- Update documentation for all user-facing changes.
- Document new functions, classes, and modules.
- Keep the README.md up to date.

## Questions?

Feel free to create an issue for any questions or concerns about contributing.

Thank you for your contributions!
