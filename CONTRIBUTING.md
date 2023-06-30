# Contributing

## Set up the Development environment

To install the development environment, please follow these steps, preferably in a Python 3.8 virtual environment.

```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

You will also have all packages related to the repository development: testing, linting, documentation etc...
pre-commit will automatically run when you commit.

(If kili was already installed in the virtual environment, remove it with `pip uninstall kili` before reinstalling it in editable mode with the -e flag.)

## Testing

To test a feature,
you can run

```bash
pytest tests/<TEST_TO_RUN>.py
```

to run all tests, simply run `pytest tests`

## Linting

The repository has pylint as linter. To run pylint checks, execute:

```bash
pylint src/kili
```

Only code rated 10.00/10 will success in the CI.

## PR names

The PR titles should follow these [guidelines](https://www.conventionalcommits.org/en/v1.0.0/)
