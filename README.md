# thin-controller

`thin-controller` is a FastAPI web app for viewing and starting or stopping AWS EC2 instances tagged with `thin_controller_managed=true`.

It can run locally with uvicorn, behind AWS Lambda via Mangum, or as a container in Fargate. The UI is a small server-rendered page backed by a handful of API endpoints.

## Overview

- FastAPI app: [thin_controller/__init__.py](thin_controller/__init__.py)
- Local CLI: [thin_controller/__main__.py](thin_controller/__main__.py)
- Lambda handler: [thin_controller/handler.py](thin_controller/handler.py)
- Models and config: [thin_controller/models.py](thin_controller/models.py)
- Terraform deployment code: [terraform/](terraform)

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

## Scheduled power control

The repository can optionally deploy a separate scheduler Lambda that runs from EventBridge every hour and enforces EC2 power state from instance tags. This scheduler is independent of the UI hosting mode, so it can run whether the app itself is deployed on Lambda or Fargate.

Terraform settings:

- `enable_scheduled_power_control`: enable or disable the scheduler module. Default `false`.
- `scheduled_power_control_expression`: EventBridge schedule expression. Default `rate(1 hour)`.

Required tags for scheduler participation:

- `thin_controller_managed=true`
- `thin-controller-timezone`: IANA timezone such as `Australia/Brisbane`
- `thin-controller-on-hours`: daily `HH-HH` 24-hour window such as `09-17` or `22-06`

Optional scheduler override:

- `thin-controller-always-on=true`
- `thin-controller-always-on=1`

Schedule rules:

- The scheduler starts `stopped` instances when the instance's local time is inside the configured window.
- The scheduler stops `running` instances when the local time is outside the configured window.
- Start hour is inclusive and end hour is exclusive.
- Overnight windows are supported, for example `22-06`.
- Instances missing either scheduling tag are ignored.
- Invalid tag values are logged and skipped.

Terraform example:

```hcl
use_fargate                    = true
enable_scheduled_power_control = true
scheduled_power_control_expression = "rate(1 hour)"
thin_controller_regions        = "ap-southeast-2,us-east-1"
```

Tag examples:

Business hours in Brisbane:

```text
thin_controller_managed=true
thin-controller-timezone=Australia/Brisbane
thin-controller-on-hours=09-17
```

Overnight window in New York:

```text
thin_controller_managed=true
thin-controller-timezone=America/New_York
thin-controller-on-hours=22-06
```

Temporary always-on override:

```text
thin_controller_managed=true
thin-controller-timezone=Australia/Brisbane
thin-controller-on-hours=09-17
thin-controller-always-on=true
```

## HTTP surface

- `GET /`: main HTML UI
- `GET /api/instances`: list managed instances across configured regions
- `POST /api/instance`: start or stop a managed instance
- `GET /api/config`: return the resolved region configuration
- `GET /up`: simple health check

The `POST /api/instance` route expects form fields for `instance_id`, `region`, and `new_state`.

## Deployment

Infrastructure lives in [terraform/](terraform). Start with [terraform/terraform.tfvars.example](terraform/terraform.tfvars.example).

Terraform supports two deployment modes:

- Lambda, using the Mangum handler in [thin_controller/handler.py](thin_controller/handler.py)
- Fargate, using the container built from [Dockerfile](Dockerfile)

The Lambda packaging flow currently installs dependencies with local `python3.13` in Terraform while targeting the AWS Lambda `python3.12` runtime.
