default:
    just --list

check: lint types test

coverage:
    uv run coverage run --source=thin_controller -m pytest
    uv run coveralls


test:
    uv run pytest

lint:
    uv run ruff check thin_controller tests

types:
    uv run mypy --strict thin_controller tests


build_container:
    docker build -t ghcr.io/yaleman/thin-controller:latest .
