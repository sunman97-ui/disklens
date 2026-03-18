# Contributing to DiskLens

Thank you for your interest in contributing to DiskLens! As an open-source project that handles file deletions, we maintain high standards for safety and code quality.

## Development Setup

1. **Prerequisites**:
   - Python 3.10 or higher.
   - [uv](https://github.com/astral-sh/uv) (recommended) or `pip`.

2. **Clone and Install**:
   ```bash
   git clone https://github.com/sunman97/disklens.git
   cd disklens
   pip install -e .[dev]
   ```

3. **Verify Installation**:
   ```bash
   pytest
   ```

## Code Quality Standards

We use **Ruff** for linting and formatting, and **Mypy** for type checking.

- **Format your code**: `ruff format .`
- **Lint your code**: `ruff check . --fix`
- **Type Check**: `mypy src/`

## Testing Policy

Any new feature or bug fix **must** include corresponding tests in the `tests/` directory. 
- Ensure your tests pass: `pytest`
- Aim for high coverage: `pytest --cov=src`

## Commit Message Convention

DiskLens uses **[Conventional Commits](https://www.conventionalcommits.org/)** to automate its versioning and release process. Please use the following prefixes for your commit messages:

- **`feat:`**: A new feature (bumps **Minor** version)
- **`fix:`**: A bug fix (bumps **Patch** version)
- **`docs:`**: Documentation-only changes
- **`style:`**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **`refactor:`**: A code change that neither fixes a bug nor adds a feature
- **`perf:`**: A code change that improves performance
- **`test:`**: Adding missing tests or correcting existing tests
- **`build:`**, **`ci:`**, **`chore:`**: Changes to our CI/CD or build scripts

If your change is a **Breaking Change**, include a `!` after the type (e.g., `feat!: rewrite scanner logic`) and provide a detailed explanation in the commit body.

## Pull Request Process

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Implement your changes and add tests.
3. Ensure all CI checks (linting, types, tests) pass locally.
4. Submit a Pull Request with a clear description of the changes and the problem they solve.

## Safety First

When modifying the scanner or deletion logic:
- Always test with mocked filesystems first.
- Never bypass the `_BLOCKED_NAMES` or `_BLOCKED_PATH_SEGMENTS` guards without significant justification and community review.

---
By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
