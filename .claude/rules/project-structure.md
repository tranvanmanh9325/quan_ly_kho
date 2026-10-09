# Project Structure and Modular Architecture

This document outlines the modular directory structure, package responsibilities, and per-object component organization of the Warehouse Management backend.

## Architectural Layout

The project adopts a modular per-object pattern under the core `warehouse` Django application, eliminating monolithic single-file bottlenecks (`models.py`, `serializers.py`, `views.py`, `tests.py`).

```text
quan_ly_kho/
├── .claude/
│   ├── rules/
│   │   ├── CLAUDE.md (index and routing)
│   │   ├── overview-and-stack.md
│   │   ├── collaboration-principles.md
│   │   ├── python-django-style.md
│   │   ├── rest-api-conventions.md
│   │   ├── database-and-orm.md
│   │   ├── data-safety-and-deletion.md
│   │   ├── security-and-secrets.md
│   │   ├── testing.md
│   │   ├── git-and-commits.md
│   │   ├── dev-commands.md
│   │   └── project-structure.md
│   └── skills/
│       ├── warehouse-domain-model/ (SKILL.md, references/)
│       ├── warehouse-api-endpoints/ (SKILL.md, references/)
│       ├── warehouse-testing/ (SKILL.md, references/)
│       ├── warehouse-db-migrations-and-safety/ (SKILL.md, references/)
│       └── warehouse-feature-workflow/ (SKILL.md, references/)
├── warehouse/
│   ├── models/
│   │   ├── __init__.py (re-exports Warehouse, Product, StockStatus)
│   │   ├── warehouse.py (Warehouse entity and properties)
│   │   └── product.py (Product entity and StockStatus choices)
│   ├── serializers/
│   │   ├── __init__.py (re-exports all serializers)
│   │   ├── warehouse.py (WarehouseSerializer)
│   │   ├── product.py (ProductSerializer)
│   │   ├── stock_adjustment.py (StockAdjustmentSerializer)
│   │   └── auth.py (UserRegisterSerializer, UserLoginSerializer)
│   ├── views/
│   │   ├── __init__.py (re-exports all viewsets and views)
│   │   ├── warehouse.py (WarehouseViewSet)
│   │   ├── product.py (ProductViewSet)
│   │   └── auth.py (RegisterView, LoginView, UserProfileView)
│   ├── services/
│   │   ├── __init__.py
│   │   └── stock_service.py (lean stock adjustment domain service)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── base.py (BaseAPITestCase and shared fixtures)
│   │   ├── test_warehouse_api.py
│   │   ├── test_product_api.py
│   │   ├── test_stock_adjustment.py
│   │   └── test_auth.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   ├── admin.py
│   ├── apps.py
│   └── urls.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── README.md
```

## Re-Export Conventions and Backward Compatibility

- **Models Re-export**: `warehouse/models/__init__.py` explicitly imports and exposes `Warehouse`, `Product`, and `StockStatus`. This guarantees that legacy imports such as `from warehouse.models import Warehouse, Product` and existing migrations remain 100% operational without regression.
- **Serializers Re-export**: `warehouse/serializers/__init__.py` re-exports all serializers for clean imports across views and admin.
- **Views Re-export**: `warehouse/views/__init__.py` re-exports all ViewSets and API views to preserve `warehouse/urls.py` routing unchanged.
- **Tests Re-export**: `warehouse/tests/__init__.py` imports all test classes so `python manage.py test` automatically discovers every test suite.
