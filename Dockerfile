FROM python:3.13-slim


ADD thin_controller /app/thin_controller
ADD README.md /app/README.md
ADD pyproject.toml /app/pyproject.toml


RUN adduser nonroot

USER nonroot

RUN pip install --user  --no-cache /app

WORKDIR /home/nonroot

EXPOSE 8000

ENTRYPOINT ["/home/nonroot/.local/bin/thin-controller", "--host", "0.0.0.0"]
