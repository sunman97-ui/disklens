# CHANGELOG


## v0.1.1 (2026-03-18)

### Bug Fixes

- Add type hints throughout codebase and update mypy configuration
  ([`6413cdf`](https://github.com/sunman97-ui/disklens/commit/6413cdfaf964e6606cad49a1879286c1831fbd90))

fix: Add type hints throughout codebase and update mypy configuration

- Add type hints throughout codebase and update mypy configuration
  ([`1485c42`](https://github.com/sunman97-ui/disklens/commit/1485c421aea3239d56b171c5122b85919c02d7e3))

- Introduce type annotations in `main.py`, `scanner.py`, `charts.py`, and `largelist.py` to improve
  static type checking and code clarity. - Update `pyproject.toml` mypy config: limit `files` to
  `main.py`, add `mypy_path = "src"`, and add overrides for `views.*` modules to relax untyped
  defs/calls. - Fix CI workflow to use `--system` flag with `uv pip install` for consistent
  environment. - Update README CI badge to specify `main` branch. - Remove duplicate `_rebuild_rows`
  method in `largelist.py`. - Ignore incidental `.coverage` binary diff.

- Ruff format previous test fail is fixed (formatted and now passing)
  ([`71e8fbe`](https://github.com/sunman97-ui/disklens/commit/71e8fbeb3632130e241a42daeb12d0aa93d0838c))


## v0.1.0 (2026-03-18)

### Features

- Initial professional release with safety guards, automated CI/CD, and dense integration test suite
  ([`d3eec6e`](https://github.com/sunman97-ui/disklens/commit/d3eec6e487ceed073b08475e96f6648e6b595c3d))
