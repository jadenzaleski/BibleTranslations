# bible-translations

<p align=center>
  <img alt="Github Created At" src="https://img.shields.io/github/created-at/jadenzaleski/bible-translations?style=flat-square&color=orange">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/jadenzaleski/bible-translations?style=flat-square">
</p>

This repo holds the python package for pulling many possible bible translations off the internet.
It also holds bundled translations in various formats available for download.

## Download

Here are all possible translations, precompiled and bundled.

| Translation | SQL | JSON | Copyright | Notes |
|-------------|-----|------|-----------|-------|
| KJV         | -   | -    | -         | -     |
|             |     |      |           |       |
|             |     |      |           |       |
|             |     |      |           |       |

## Install

You can Install from PyPI

```bash
pip install bible-translations 
```

The package provides a CLI command:

```bash
bt
# or
bible-translations
```

### Install from local source

Clone the repo and install in editable mode:

```bash
git clone https://github.com/jadenzaleski/bible-translations.git
cd bible-translations
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

The last command (`pip install -e ".[dev]"`) automatically installs the package *and* any tools listed under
`[project.optional-dependencies].dev` (e.g. `pytest`, `ruff`). The `-e` flag creates a "symlink" so changes you make to
`src/bible_translations/` are immediately available when importing the package.

### Build from a local source

Generate a wheel and source distribution:

```bash
python -m build
```

This creates a dist/ folder with:

- .whl → wheel (binary distribution)
- .tar.gz → source distribution

You can install the wheel to test locally:

```bash
pip install dist/bible_translations*.whl
```

### Run Tests

```bash
pip install pytest
pytest
```

## Usage

How to use the package here.

## Changelog

You can find all the change information [here](CHANGELOG.md).

## Contributing

Be sure to check out the [bible-translations project](https://github.com/users/jadenzaleski/projects/7) to see where you
can help!

Guidelines for contributing can be found [here](CONTRIBUTING.md).

## Disclaimer

Please read our disclaimer [here](DISCLAIMER.md).

