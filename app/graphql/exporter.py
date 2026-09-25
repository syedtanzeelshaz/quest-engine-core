"""
Schema Exporter Script.

Compiles the current Strawberry GraphQL schema and exports it as an SDL (.graphql) file.
Executed directly via:
    python -m app.graphql.exporter [output_path]
"""
import sys
from pathlib import Path

from app.api.graphql.schema import schema
from app.graphql.common.constants import DEFAULT_SCHEMA_OUTPUT_PATH
from app.util.logger import log


def export_schema(output_path: str = DEFAULT_SCHEMA_OUTPUT_PATH) -> None:
    """Export the compiled Strawberry schema as raw SDL."""
    sdl = schema.as_str()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(sdl)
    log.info("Schema successfully exported to %s — %d lines", output_path, len(sdl.splitlines()))


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCHEMA_OUTPUT_PATH
    export_schema(target)


# Direct execution entrypoint (e.g. `python -m app.graphql.exporter [output_path]`)
if __name__ == "__main__":
    main()

