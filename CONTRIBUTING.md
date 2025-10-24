# Contributing
Thanks for your interest in contributing.

## Steps
1. Fork the repo and create a new branch (preferably linking to the issue):
   ```bash
   git checkout -b 42-your-feature
   ```
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run the linter and formatter before committing ([ruff docs](https://docs.astral.sh/ruff/linter/)):
   ```bash
   ruff check . --fix
   ruff format
   ```
4. Run tests to verify your changes:
   ```bash
   pytest
   ```
5. Commit with the following conventional style:
   * `feat:` add feature  
   * `fix:` resolve bug  
   * `docs:` update documentation  
6. Push and open a Pull Request to `main`.
7. Link related issues (e.g., `Closes #42`).

## Guidelines
* Keep PRs small and focused.
* Match the existing code style (Ruff-enforced).
* Add or update tests when needed.
* Update documentation if behavior changes.

By contributing, you agree your code is under the project’s [license](LICENSE).