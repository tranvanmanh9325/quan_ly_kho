---
paths:
  - "**/models/**"
  - "**/services/**"
---

# Database and ORM Guidelines

This document outlines query optimization patterns, data integrity mechanisms, model lifecycle hooks, and migration management standards for Django ORM and PostgreSQL.

## Query Optimization Standards

- **Preventing N+1 Queries**:
  - Always use `select_related('warehouse')` when querying product records or related foreign key collections.
  - In ViewSets, configure `queryset = Product.objects.select_related('warehouse').all()` to ensure single SQL JOIN execution.
- **Database-Level Aggregation**:
  - Compute summary statistics and inventory metrics at the database level using `django.db.models` aggregation functions (`Sum`, `Count`, `Avg`).
  - Never iterate through entire QuerySets in Python application memory to compute sums, counts, or capacity utilization.

## Data Integrity and Model Validation

- **Validation in `clean()`**:
  - Encapsulate cross-field and relational validation rules within the model's `clean()` method (e.g. verifying that adding product quantity will not exceed `warehouse.capacity`).
  - Validating in `clean()` ensures invariants are enforced consistently across API serializer calls, custom scripts, and Django Admin forms.
- **Preserving Model Invariants in `save()`**:
  - Call `self.full_clean()` explicitly within `save()` before committing the record to the database whenever model-level invariants must be guaranteed.
- **Atomic State Transitions**:
  - Maintain the stock status state machine (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`) inside `save()` so status reflects inventory quantity automatically across all write pathways.

## Migrations Workflow and Safety

- **Pre-Application Review**:
  - Always inspect generated migration files before executing `python manage.py migrate`. Verify table names, index creation, constraints, and default values.
- **Applied Migration Immutability**:
  - Never manually modify migration files that have already been executed on any shared database.
  - To introduce schema changes, create forward-only migration files using `python manage.py makemigrations`.
- **Integrity Validation**:
  - Before committing code, verify migration integrity with `python manage.py makemigrations --check --dry-run` to ensure no drift between models and migration files.
