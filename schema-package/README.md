# @quest-engine/schema

This package contains the official GraphQL Schema Definition Language (SDL) for Quest Engine Core.

## Usage

Generated automatically from the backend using:
```bash
# Using the uv run script shortcut
uv run export-schema

# Or via Python module execution
uv run python -m app.graphql.exporter
```

Frontend applications should consume `schema.graphql` via GraphQL Codegen (`@graphql-codegen/cli`).

