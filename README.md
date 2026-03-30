# thin-controller

`thin-controller` is a FastAPI web app for viewing and starting or stopping AWS EC2 instances tagged with `thin_controller_managed=true`.

It can run locally with uvicorn, behind AWS Lambda via Mangum, or as a container in Fargate. The UI is a small server-rendered page backed by a handful of API endpoints.

## Overview

- FastAPI app: [thin_controller/__init__.py](/Users/yaleman/Projects/thin-controller/thin_controller/__init__.py)
- Local CLI: [thin_controller/__main__.py](/Users/yaleman/Projects/thin-controller/thin_controller/__main__.py)
- Lambda handler: [thin_controller/handler.py](/Users/yaleman/Projects/thin-controller/thin_controller/handler.py)
- Models and config: [thin_controller/models.py](/Users/yaleman/Projects/thin-controller/thin_controller/models.py)
- Terraform deployment code: [terraform/](/Users/yaleman/Projects/thin-controller/terraform)

## Requirements

- Python 3.12 or newer
- `uv` for dependency management and running commands
- AWS credentials available to the app when listing or changing EC2 instances

## Local development

Install dependencies:

```bash
uv sync
```

Run the development server with reload:

```bash
uv run thin-controller --reload
```

Run without reload:

```bash
uv run thin-controller
```

Useful development commands:

```bash
just check
just test
just lint
just types
just coverage
just build_container
```

## Configuration

The application reads configuration from environment variables using the `THIN_CONTROLLER_` prefix.

`THIN_CONTROLLER_REGIONS`

- Comma-delimited list of AWS regions to scan and control.
- If unset, the app defaults to all EC2 regions returned by boto3.

Operational rules:

- Only instances tagged with `thin_controller_managed=true` are shown and controlled.
- The UI only allows `stopped -> start` and `running -> stop`.
- Other instance states are visible but not actionable.

## HTTP surface

- `GET /`: main HTML UI
- `GET /api/instances`: list managed instances across configured regions
- `POST /api/instance`: start or stop a managed instance
- `GET /api/config`: return the resolved region configuration
- `GET /up`: simple health check

The `POST /api/instance` route expects form fields for `instance_id`, `region`, and `new_state`.

## Deployment

Infrastructure lives in [terraform/](/Users/yaleman/Projects/thin-controller/terraform). Start with [terraform/terraform.tfvars.example](/Users/yaleman/Projects/thin-controller/terraform/terraform.tfvars.example).

Terraform supports two deployment modes:

- Lambda, using the Mangum handler in [thin_controller/handler.py](/Users/yaleman/Projects/thin-controller/thin_controller/handler.py)
- Fargate, using the container built from [Dockerfile](/Users/yaleman/Projects/thin-controller/Dockerfile)

The Lambda packaging flow currently installs dependencies with local `python3.13` in Terraform while targeting the AWS Lambda `python3.12` runtime.
