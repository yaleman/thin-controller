"""thin-controller main"""

import click
import uvicorn


@click.command()
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def cli(reload: bool = False) -> None:
    """Run the Thin Controller server"""

    if reload:
        uvicorn.run(
            "thin_controller:app",
            host="localhost",
            port=8000,
            reload=True,
            reload_dirs=["thin_controller"],  # because watching too much gets hungry
        )
    else:
        uvicorn.run("thin_controller:app", host="localhost", port=8000)


if __name__ == "__main__":
    cli()
