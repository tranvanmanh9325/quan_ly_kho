# Data Safety and Database Deletion Policy

This document establishes the official database safety policy, data retention rules, forbidden operations for AI agents, and emergency recovery procedures for PostgreSQL and Django ORM.

## Business Data Deletion Policy

### Soft Delete versus Hard Delete

- **Core Business Entities**: Physical warehouses (`Warehouse`) and inventory items (`Product`) represent critical business assets with financial, accounting, and audit trail value.
- **Soft Delete Standard**: Core business entities must adhere to the Soft Delete design pattern (`is_deleted = models.BooleanField(default=False)` and `deleted_at = models.DateTimeField(null=True, blank=True)`). Data must remain in PostgreSQL to preserve inventory audit history, transaction records, and inventory counting accuracy.
- **Hard Delete Scope**: Hard deletion (`DELETE FROM`) is strictly restricted to ephemeral, transient data such as expired authentication tokens (`authtoken_token`) and temporary cache sessions.
- **Architectural Boundary**: Per project constraints, AI agents must not alter existing runtime models or schemas for soft deletion without explicit written authorization from the Engineering Manager.

### Cascade Deletion Analysis and Foreign Key Constraints

- **Existing Cascade Risk**: The relationship `Product.warehouse` currently defines `on_delete=models.CASCADE`. Under this setting, deleting a single `Warehouse` instance triggers the immediate, irreversible deletion of all associated `Product` inventory records.
- **CASCADE vs PROTECT vs SET_NULL**:
  - `models.CASCADE`: High business risk. Accidental warehouse removal destroys all inventory ledger records.
  - `models.PROTECT`: Recommended enterprise standard. Prevents warehouse deletion if active products are assigned (`ProtectedError`), forcing explicit inventory re-allocation or clearance first.
  - `models.SET_NULL`: Unsuitable for physical inventory because products cannot exist detached from a warehouse facility without breaking capacity invariants.
- **Architecture Recommendation**: The Engineering Manager is formally advised to migrate `Product.warehouse` to `models.PROTECT` in future schema versions.

## Forbidden Destructive Operations for AI Agents

AI agents are strictly forbidden from executing any of the following operations without explicit, prior human engineering authorization:

1. **Database Destruction**: Running `dropdb`, `DROP DATABASE`, `DROP SCHEMA`, or `DROP TABLE`.
2. **Database Flush**: Running `python manage.py flush` (wipes all table rows across the database).
3. **Migration Zeroing and Reversal**: Running `python manage.py migrate <app> zero` or rolling back migrations to earlier states.
4. **Deleting Migration Files**: Deleting or renaming existing migration files (e.g. `rm warehouse/migrations/0001_initial.py`).
5. **Development Database Reset**: Deleting, recreating, or zeroing the active development database (`quan_ly_kho_db`).
6. **Low-Level Truncation**: Issuing SQL `TRUNCATE` or `TRUNCATE TABLE ... CASCADE` statements.
7. **Unconstrained Bulk Deletion**: Issuing `Model.objects.all().delete()` or broad QuerySet deletions without explicit `filter()` boundaries and pre-counted impact confirmation.
8. **Editing Applied Migrations**: Manually altering Python migration code that has already been executed against any database.

## Safe Operating Procedure for Sensitive Database Operations

Whenever an authorized structural change, migration repair, or data maintenance task is required, AI agents and engineers must execute the following 5-step Standard Operating Procedure (SOP):

### Step 1: Backup First

Before modifying any data or applying schema revisions, generate a full binary backup of the PostgreSQL database:

```powershell
pg_dump -U postgres -h localhost -p 5432 -d quan_ly_kho_db -F c -b -v -f backup_quan_ly_kho.dump
```

Verify that the backup file exists and has a non-zero byte size before proceeding.

### Step 2: Test on Isolated Sandbox Database

Execute migration scripts and data transformations on a separate local test database before applying them to development.

### Step 3: Verify Environment Context

Confirm environment variables (`DB_NAME`, `DB_HOST`, `DB_PORT`, `DEBUG`). Never execute maintenance scripts against shared staging or production environments.

### Step 4: Require Explicit Human Confirmation

Present a complete execution plan to the human engineer including:

- Intended command or script
- Specific tables and estimated row count affected
- Location and verification status of the backup file
- Potential side effects and downtime window

Wait for explicit written human confirmation before execution.

### Step 5: Prepare and Verify Rollback Plan

Document the exact recovery command to restore state should any anomaly occur:

```powershell
pg_restore -U postgres -h localhost -p 5432 -d quan_ly_kho_db -c -v backup_quan_ly_kho.dump
```

## Test Database Isolation Principles

- **Automatic Isolation**: Running `python manage.py test` automatically provisions a dedicated, ephemeral test database (`test_quan_ly_kho_db`).
- **Complete Segregation**: All test insertions, updates, and rollbacks execute exclusively within the test database and tear down automatically upon suite completion.
- **Zero Pollution**: Automated test scripts must never connect directly to or issue write operations against the active development database (`quan_ly_kho_db`).
