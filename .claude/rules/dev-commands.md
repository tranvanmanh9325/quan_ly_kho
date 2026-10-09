# Standard Development Commands

This document catalogues the standard terminal commands and scripts used for development, database maintenance, testing, verification, and code quality checks.

## Virtual Environment Activation

On Windows PowerShell:

```powershell
cd D:\GitHub\codegym\quan_ly_kho
.\venv\Scripts\Activate.ps1
```

## Running the Development Server

Start the local Django development server on port 8000:

```powershell
python manage.py runserver 8000
```

## Database and Schema Operations

```powershell
# Check for model changes and create forward migration files
python manage.py makemigrations

# Verify that no unapplied model schema changes exist (must report no changes)
python manage.py makemigrations --check --dry-run

# Apply all pending migrations to PostgreSQL
python manage.py migrate

# Seed sample warehouses, products, and admin users
python manage.py seed_data
```

## Automated Testing Commands

```powershell
# Run the entire test suite across all modular test modules
python manage.py test

# Run specific test modules individually
python manage.py test warehouse.tests.test_warehouse_api
python manage.py test warehouse.tests.test_product_api
python manage.py test warehouse.tests.test_stock_adjustment
python manage.py test warehouse.tests.test_auth
```

## System Integrity and Verification

```powershell
# Perform Django system configuration and model validation checks
python manage.py check

# Run markdownlint on all documentation, rules, and skills
npx markdownlint-cli2 "README.md" ".claude/**/*.md"
```
