# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

thin-controller is a FastAPI-based web application that controls AWS EC2 instances via AWS Lambda. It allows starting/stopping EC2 instances tagged with `thin_controller_managed=true` through a web interface.

## Architecture

- **FastAPI Application** (`thin_controller/__init__.py`): Main application with REST API endpoints and static file serving
- **AWS Lambda Handler** (`thin_controller/handler.py`): Mangum wrapper that adapts FastAPI for Lambda execution
- **Models** (`thin_controller/models.py`): Pydantic models for AWS instances and configuration
  - `AWSInstance`: Parses EC2 instance data from boto3 responses
  - `Config`: Application configuration with environment variable support (prefix: `THIN_CONTROLLER_`)
- **CLI** (`thin_controller/__main__.py`): Click-based CLI for running uvicorn locally
- **Terraform** (`terraform/`): Infrastructure as Code for deploying to AWS Lambda with Lambda layers

## Development Commands

### Running the Application
```bash
# Start development server with auto-reload
uv run thin-controller --reload

# Start without reload
uv run thin-controller
```

### Testing and Quality Checks
```bash
# Run all checks (lint + types + test)
just check

# Run tests
just test
# or
uv run pytest

# Run linting
just lint
# or
uv run ruff check thin_controller tests

# Run type checking
just types
# or
uv run mypy --strict thin_controller tests

# Run coverage
just coverage
```

### Container
```bash
# Build Docker container
just build_container
# or
docker build -t ghcr.io/yaleman/thin-controller:latest .
```

## Key Configuration

- **Python Version**: Requires Python 3.12+
- **Package Manager**: Uses `uv` (not poetry)
- **AWS Configuration**: Set `THIN_CONTROLLER_REGIONS` environment variable to control which AWS regions to scan (defaults to all EC2 regions)
- **Managed Instances**: Only EC2 instances with tag `thin_controller_managed=true` are controllable

## AWS Lambda Deployment

The Terraform module creates:
- Lambda layer with dependencies (built using `pip install` into `thin_controller_layer/`)
- Lambda function using the `terraform_lambda` module (v1.0.8)
- Python 3.12 runtime with 30-second timeout

The layer building process uses `python3.13` locally but targets `python3.12` runtime in Lambda.

## State Management

Instance state changes follow strict rules in `STATE_CHANGES`:
- `running` → can only `stop`
- `stopped` → can only `start`
- Other states (`pending`, `shutting-down`, `terminated`, `stopping`) are not directly actionable
