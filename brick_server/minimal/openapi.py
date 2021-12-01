"""
Generate the openapi schema
"""

from pathlib import Path
from typing import Optional

import click
import json

from brick_server.minimal.app import app


@click.command("openapi")
@click.option("-o", "--output", type=click.Path(), required=False, default=None)
def main(output: Optional[str]) -> None:
    openapi_json = json.dumps(app.openapi(), indent=2)
    if output is None:
        print(openapi_json)
    else:
        with Path(output).open("w", encoding="utf-8") as f:
            f.write(openapi_json)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
