# Database Safety Runbooks Reference

This reference document provides operational runbooks, backup/restore commands, incident recovery workflows, and pre-execution safety checklists for PostgreSQL in the Warehouse Management system.

## PostgreSQL Backup and Restore Runbook

### Creating a Complete Binary Backup

Run `pg_dump` with custom archive format (`-F c`), blobs (`-b`), and verbose logging (`-v`):

```powershell
pg_dump -U postgres -h localhost -p 5432 -d quan_ly_kho_db -F c -b -v -f backup_quan_ly_kho_$(Get-Date -Format 'yyyyMMdd_HHmmss').dump
```

Verification command:

```powershell
Get-Item backup_quan_ly_kho_*.dump | Select-Object Name, Length, LastWriteTime
```

Ensure the output confirms the backup file exists and has a size greater than 0 bytes.

### Restoring from Binary Backup

To restore the database cleanly in case of accidental corruption or invalid migration:

```powershell
# Drop and recreate schema cleanly
pg_restore -U postgres -h localhost -p 5432 -d quan_ly_kho_db -c -v backup_quan_ly_kho_20261009_080000.dump
```

## Migration Drift Diagnostic Runbook

When investigating schema drift or unapplied model modifications:

```powershell
# 1. Inspect model differences against migrations
python manage.py makemigrations --check --dry-run

# 2. Show applied status across all app migrations
python manage.py showmigrations

# 3. Inspect raw SQL generated for an existing migration
python manage.py sqlmigrate warehouse 0001
```

## Pre-Execution Safety Checklist

Before executing any script that alters records or modifies tables, verify:

- [ ] A verified binary backup (`pg_dump`) was created within the last 15 minutes.
- [ ] The command has been tested against an isolated test database.
- [ ] Current database target is confirmed (`quan_ly_kho_db`, not staging or production).
- [ ] Number of rows expected to be modified has been calculated via `.count()`.
- [ ] The human engineer has provided written confirmation of the plan.
- [ ] The restore command is verified and ready for execution if an anomaly occurs.
