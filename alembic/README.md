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

* `env.py`: Configuration script loaded during every migration; dynamically reads `settings.ALEMBIC_DATABASE_URL` and routes versioning into the `alembic` schema.

* `script.py.mako`: The Mako template blueprint used when generating new migration script files.
* `versions/`: Directory containing individual chronological version files (e.g., identity schema creation, tenant tables, audit logs).

---

## Workflow: How to Add a New Database Migration

### Step 1: Create a New Blank Revision Script

Run the following CLI command from the project root to generate a new timestamped migration file under `alembic/versions/`:

    alembic revision -m "describe your migration here"

* **What it does:** Generates an empty migration script using `script.py.mako` (i.e., `alembic/versions/YYYYMMDDHHMMSS_describe_your_migration_here.py`), with a unique revision ID and the appropriate `down_revision` mapping.
* **Author metadata:** While generating the migration file, the template reads the current Git configuration (git config --get user.name and git config --get user.email) and stores the values in the generated script as author_name and author_email. This author information is for migration-file metadata only. It is not stored in `alembic.alembic_version` db table and is not used by Alembic to determine migration identity or execution state.

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

    # author metadata stuff ...


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


### Step 3: Apply the Migration

Migrations can be applied either manually through the CLI or automatically during application startup. Make sure DB is accessible and has initial `alembic` schema in it to apply migration successfully.

#### Option A: Manual CLI Execution

Run from the project root:

    alembic upgrade head

This applies all pending migrations up to the latest revision and records that revision in `alembic.alembic_version` db table.

#### Option B: Automatic Application Startup

In production, migrations can also be triggered automatically as part of the application bootstrap flow (see `app/core/initialization/db_migrations.py`)
The backend initialization logic invokes Alembic programmatically, allowing the database to be migrated automatically when the application starts.

---

## Notes

### Common Alembic Commands

| Command | Description |
|---|---|
| `alembic current` | Shows the migration revision currently recorded in the database. |
| `alembic upgrade head` | Applies all pending migrations up to the latest revision (`head`). |
| `alembic upgrade +1` | Applies the next migration revision in the migration chain. |
| `alembic downgrade -1` | Reverts the most recently applied migration. |
| `alembic revision -m "message"` | Creates a new blank migration script. |
| `alembic history` | Displays the migration history and revision chain. |
| `alembic heads` | Shows the current migration head revision(s). |
| `alembic show <revision>` | Displays details of a specific migration revision. |

Run these commands from the project root, where `alembic.ini` is located (not inside the alembic directory)

**Important:** 
 - `alembic revision` only creates a migration file; it does **not** modify the database. The database is changed only when a migration is executed through `alembic upgrade` or the application's startup migration flow.
 - Once a migration has been applied to a shared environment, do not modify its `revision` or `down_revision` values. Migration revisions form Alembic's migration graph, while `alembic.alembic_version` stores the database's current position in that graph.

