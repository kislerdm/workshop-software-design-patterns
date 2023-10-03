# Marketing campaign manager API - Workshop Demo - Python

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](README.md)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## How to contribute

### Prerequisites

- Python >=3.10,<3.12
- gnuMake

### Setup

Follow the steps to initialize development environment:

1. Clone the repo and navigate to the directory:

```commandline
git clone git@github.com:kislerdm/workshop-software-design-patterns.git && cd python
```

2. Create and activate a Python virtual environment:

```commandline
python -m venv .venv && source .venv/bin/activate
```

3. Setup local development environment:

```commandline
make localenv
```

### Commands

- List all available commands:

```commandline
make help
```

- Run unit tests:

```commandline
make tests
```

- Run linters and type checkers, and apply fixes:

```commandline
make lint
```

- Run unit tests for all supported Python versions (**note** that _Docker v23+_ is required for this step):

```commandline
make tests-all
```
