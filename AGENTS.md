# AGENTS.md

Repository guidance for coding agents working in `thin-controller`.

## Project overview

`thin-controller` is a Python 3.12+ FastAPI application for viewing and controlling AWS EC2 instances from a small web UI. It is packaged as:

- a local web app served by uvicorn
- an AWS Lambda handler via Mangum
- a container image used by the Fargate deployment path

The app only acts on EC2 instances tagged with `thin_controller_managed=true`.

## Important paths

- `thin_controller/__init__.py`: FastAPI app, static asset routes, instance list/update APIs, health check
- `thin_controller/__main__.py`: CLI entrypoint for local development via `thin-controller`
- `thin_controller/handler.py`: Lambda handler wrapper
- `thin_controller/models.py`: Pydantic models and environment-backed config
- `thin_controller/static/`: HTML and CSS for the built-in UI
- `tests/`: pytest coverage for API, CLI, and model parsing
- `terraform/`: AWS deployment code for Lambda and Fargate

## Workflow

- Use `uv` for dependency management and command execution.
- Use `just` targets when they match the task.
- Prefer small, direct changes over new abstractions.

Common commands:

```bash
uv sync
uv run thin-controller --reload
just test
just lint
just types
just check
just coverage
just build_container
```

## Runtime and behavior

- `THIN_CONTROLLER_REGIONS` controls which AWS regions are scanned. If unset, the app defaults to all EC2 regions returned by boto3.
- AWS credentials must be available to the running process for EC2 reads and state changes.
- Allowed state transitions are intentionally narrow:
  - `stopped -> start`
  - `running -> stop`
- Other EC2 states are displayed but not actionable.

## Editing guidance

- Preserve the current FastAPI and Pydantic style unless there is a clear reason to refactor.
- Keep the UI simple. It is a static HTML page using htmx and Nunjucks, not a frontend app framework.
- Prefer updating tests alongside behavior changes.
- Avoid broad refactors unless they directly reduce local complexity.
- Do not edit generated or vendored Terraform packaging artifacts unless the task is specifically about deployment packaging:
  - `terraform/thin_controller_layer/`
  - `terraform/thin_controller_layer.zip`
  - `terraform/thin_controller.zip`

## Deployment notes

- Terraform supports two hosting modes:
  - Lambda via `thin_controller/handler.py`
  - Fargate using `ghcr.io/yaleman/thin-controller:latest`
- The Lambda packaging step currently installs dependencies with local `python3.13` while targeting the AWS Lambda `python3.12` runtime.
