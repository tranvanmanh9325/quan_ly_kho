---
paths:
  - "**/tests/**"
---

# Automated Testing Standards and Matrix

This document defines automated test architecture, APITestCase conventions, the modular test package structure, and coverage matrices for the Warehouse Management Backend.

## Test Package Architecture

All automated test suites must reside in the modular test package `warehouse/tests/` rather than a single monolithic file. The package is organized as follows:

- `warehouse/tests/__init__.py`: Package entry point exposing all test modules for Django test runner auto-discovery.
- `warehouse/tests/base.py`: Shared base class `BaseAPITestCase` inheriting from `rest_framework.test.APITestCase`. Provisions standard test fixtures, admin and staff users, authentication tokens, sample warehouses, and common assertion helpers.
- `warehouse/tests/test_warehouse_api.py`: Tests covering warehouse CRUD operations, listing, details, capacity constraints, 401 authentication checks, and 404 not found cases.
- `warehouse/tests/test_product_api.py`: Tests covering product CRUD operations, category and status query filtering, search filters, SKU uniqueness, and capacity validation rejections.
- `warehouse/tests/test_stock_adjustment.py`: Tests covering atomic stock movements (`IMPORT` and `EXPORT`), stock insufficiency rejections, capacity threshold rejections, and state machine transitions.
- `warehouse/tests/test_auth.py`: Tests covering authentication endpoints (`/api/v1/auth/register/`, `/api/v1/auth/login/`, and `/api/v1/auth/me/`).
- `warehouse/tests/test_concurrency.py`: High-concurrency race condition tests using `TransactionTestCase` on real PostgreSQL (testing 50 parallel workers for stock export without negative balance, concurrent imports without capacity overflow, and deadlock freedom).

## APITestCase Implementation Standards

- **Base Class**: Always inherit from `BaseAPITestCase` (or `rest_framework.test.APITestCase`) for API tests. For multi-threaded concurrency tests with real transactions, inherit from `django.test.TransactionTestCase`.
- **Client Configuration**: Use `self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')` to authenticate API calls.
- **Explicit Assertions**:
  - Assert exact HTTP status codes using `rest_framework.status` constants (e.g. `status.HTTP_200_OK`, `status.HTTP_400_BAD_REQUEST`).
  - Verify JSON payload structure and specific response error messages.
  - Verify database persistence state directly via ORM queries after API mutations.

## Required Test Coverage Matrix

Every new endpoint, model constraint, or service modification must provide coverage across the following scenarios:

- **Happy Path**: Successful creation (`201 Created`), retrieval and update (`200 OK`), and deletion (`204 No Content`).
- **Validation Rejection**: Negative quantities, zero values where positive required, blank required fields, and duplicate unique constraints (`400 Bad Request`).
- **Capacity Overflow**: Adding or importing items exceeding `Warehouse.capacity` must be rejected (`400 Bad Request`).
- **Insufficient Inventory**: Exporting quantities greater than current inventory balance must be rejected (`400 Bad Request`).
- **Authentication Safeguards**: Accessing protected write operations without a valid token must be denied (`401 Unauthorized`).
- **Resource Lookups**: Requesting non-existent primary keys must return clear not-found responses (`404 Not Found`).
- **Concurrency & Race Conditions**: High-contention parallel transactions on PostgreSQL must guarantee invariant preservation (no negative inventory, no capacity breach).
- **State Machine Lifecycle**: Verify automatic status transitions upon quantity changes:
  - `quantity == 0` -> `OUT_OF_STOCK`
  - `0 < quantity <= 10` -> `LOW_STOCK`
  - `quantity > 10` -> `IN_STOCK`

## Test Execution Commands

```powershell
# Run all 72 tests across the entire test package
python manage.py test

# Run a specific test module
python manage.py test warehouse.tests.test_warehouse_api
python manage.py test warehouse.tests.test_product_api
python manage.py test warehouse.tests.test_stock_adjustment
python manage.py test warehouse.tests.test_auth
python manage.py test warehouse.tests.test_concurrency
```
