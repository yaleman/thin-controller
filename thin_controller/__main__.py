"""thin-controller main"""

import click
import uvicorn


@click.command()
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--host", default="localhost", help="Host to run the server on")
@click.option("--port", default=8000, help="Port to run the server on")
def cli(reload: bool = False, host: str = "localhost", port: int = 8000) -> None:
    """Run the Thin Controller server"""

    if reload:
        uvicorn.run(
            "thin_controller:app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=["thin_controller"],  # because watching too much gets hungry
        )
    else:
        uvicorn.run("thin_controller:app", host=host, port=port)


if __name__ == "__main__":
    cli()
