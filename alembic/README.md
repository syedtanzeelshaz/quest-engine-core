# Quest Engine Core - Database Migrations (Alembic)

This directory contains the database schema migration scripts and configuration for the Quest Engine, managed via **Alembic**.

---

## What is Alembic & Why Are We Using It?

**Alembic** is a lightweight database migration tool written by the author of SQLAlchemy. It allows developers to manage, evolve, and version-control database schema changes over time in a safe, repeatable, and programmatic manner.

### Key Architectural Benefits in Quest Engine:
1. **Schema Evolution:** It ensures that database schemas across different environments (local development, staging, production) stay perfectly synchronized with our domain models.
2. **Dedicated Version Metadata:** Migration tracking (`alembic_version`) is isolated within its own dedicated `alembic` schema, keeping our business domains (eg: `identity` , `tenant` etc.) pristine.
3. **Automated Startup Provisioning:** Migrations are executed programmatically on application bootstrap (`app/core/initialization/db_migrations.py`).
4. **Temporal Audit Tracking:** Seamlessly provisions complex multi-tenant tables, composite foreign keys, GIST exclusion constraints, and Hibernate/Envers-style temporal audit (`_aud`) counterparts.

---

## Directory Structure

* `env.py`: Configuration script loaded during every migration; dynamically reads `settings.DATABASE_URL` and routes versioning into the `alembic` schema.
* `script.py.mako`: The Mako template blueprint used when generating new migration script files.
* `versions/`: Directory containing individual chronological version files (e.g., identity schema creation, tenant tables, audit logs).

---

## Workflow: How to Add a New Database Migration

Always run Alembic commands from the **root directory of the project** (where `alembic.ini` is located), **not** from inside the `alembic/` folder.

### Step 1: Create a New Blank Revision Script

Run the following CLI command to generate a new timestamped migration file under `alembic/versions/`:

    alembic revision -m "describe your migration here"

* **What it does:** Generates an empty migration script using `script.py.mako`, with a unique revision ID and the appropriate `down_revision` mapping.

---

### Step 2: Write Your Migration Logic

Open the newly created file inside `alembic/versions/` and implement the required schema changes inside the `upgrade()` and `downgrade()` functions.

Prefer **Alembic's `op.*` operations** instead of raw SQL whenever a suitable operation is available.

Common operations include:

- `op.create_table()`
- `op.drop_table()`
- `op.add_column()`
- `op.drop_column()`
- `op.alter_column()`
- `op.create_index()`
- `op.drop_index()`

For example:

    from alembic import op
    import sqlalchemy as sa

    # revision identifiers stuff ...


    def upgrade() -> None:
        op.add_column(
            "example",
            sa.Column("description", sa.Text(), nullable=True),
            schema="tenant",
        )


    def downgrade() -> None:
        op.drop_column(
            "example",
            "description",
            schema="tenant",
        )


Use `op.execute()` only when the required operation cannot be expressed cleanly using Alembic's standard operations, such as database-specific features or custom SQL.

---

### Step 3: Apply the Migration

Migrations can be applied either manually through the CLI or automatically during application startup. Make sure DB is accessible to apply migration successfully.

#### Option A: Manual CLI Execution

Run from the project root:

    alembic upgrade head

This applies all pending migrations up to the latest revision and records the current revision in `alembic.alembic_version`.

#### Option B: Automatic Application Startup

In production, migrations can also be triggered automatically as part of the application bootstrap flow (see app/core/initialization/db_migrations.py)
The backend initialization logic invokes Alembic programmatically, allowing the database to be migrated automatically when the application starts.
