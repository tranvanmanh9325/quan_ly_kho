---
name: warehouse-db-migrations-and-safety
description: Use this skill when managing Django database migrations, schema evolution, data deletion policies (soft delete vs hard delete), cascade deletion risks, database backups, or preventing destructive database operations.
---

# Warehouse Database Migrations and Safety Skill

This skill defines migration protocols, schema integrity safeguards, data deletion policies, cascade deletion hazard mitigations, and emergency backup/recovery runbooks for PostgreSQL.

## Django Migration Protocols

- **Immutability of Applied Migrations**: Migration files that have already been applied to any shared environment (such as `0001_initial.py`) must never be modified directly.
- **Forward-Only Migration Flow**: Schema additions or modifications must always be introduced via new forward migration files:
  1. Modify model definitions in `warehouse/models/`.
  2. Run `python manage.py makemigrations`.
  3. Inspect the newly generated migration file in `warehouse/migrations/`.
  4. Apply migrations: `python manage.py migrate`.
- **Zero-Drift Invariant Check**: During refactoring or modularization, verify that no unexpected schema modifications were triggered:

```powershell
python manage.py makemigrations --check --dry-run
```

The output must confirm: `No changes detected`.

## Data Deletion Policy and Invariants

### Soft Delete versus Hard Delete

- **Core Assets**: Warehouses and products are physical assets tied to legal, financial, and inventory auditing requirements.
- **Enterprise Standard**: Business records should use Soft Delete (`is_deleted`, `deleted_at`) to retain inventory history for audit trails and reconciliations.
- **Hard Deletion**: Restricted exclusively to transient session and token data.
- **Authority Constraint**: AI agents must never modify runtime model schemas or delete behaviors without explicit written sign-off from the Engineering Manager.

### Foreign Key Cascade Risk

- **Current Setting**: `Product.warehouse` currently specifies `on_delete=models.CASCADE`.
- **Operational Hazard**: Deleting a `Warehouse` row cascades to delete all linked `Product` rows instantly and irrevocably.
- **Enterprise Mitigation**: Migrate to `models.PROTECT` so attempting to delete an occupied warehouse raises `ProtectedError` and fails safely.

## 8 Forbidden Destructive Operations for AI Agents

AI agents are strictly prohibited from executing the following operations without explicit written human authorization:

1. Running `dropdb`, `DROP DATABASE`, `DROP SCHEMA`, or `DROP TABLE`.
2. Running `python manage.py flush`.
3. Running `python manage.py migrate <app> zero` or rolling back migrations.
4. Deleting migration files under `warehouse/migrations/`.
5. Resetting or truncating the development database (`quan_ly_kho_db`).
6. Issuing raw SQL `TRUNCATE` or `TRUNCATE TABLE ... CASCADE`.
7. Running unconstrained bulk deletes (e.g. `Product.objects.all().delete()`).
8. Manually editing applied migration files.

## 5-Step Safe Operating Procedure (SOP)

When a sensitive or destructive database intervention is officially authorized, follow this sequence:

1. **Backup First**: Dump PostgreSQL binary archive using `pg_dump`.
2. **Test in Isolated Sandbox**: Rehearse changes against a separate test database.
3. **Verify Environment**: Verify target database connection parameters (`DB_NAME`).
4. **Explicit Human Confirmation**: Present execution plan, affected row counts, and risks to the human engineer.
5. **Rollback Plan**: Prepare and verify `pg_restore` command before proceeding.

## Detailed Runbooks Reference

For complete `pg_dump` and `pg_restore` commands, database reset runbooks, and incident response checklists, see [Safety Runbooks Reference](references/safety-runbooks.md).
