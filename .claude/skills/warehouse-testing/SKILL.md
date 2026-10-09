---
name: warehouse-testing
description: Use this skill when creating, structuring, running, or fixing automated tests, APITestCase test suites, authentication test fixtures, HTTP status assertions, or test matrix validation for the warehouse management backend.
---

# Warehouse Testing Skill

This skill defines the test engineering architecture, `APITestCase` patterns, package organization, test fixtures, and validation matrices for the Warehouse Management Backend.

## Test Package Organization

All tests must be placed inside the modular `warehouse/tests/` package rather than a single monolithic file:

```text
warehouse/tests/
├── __init__.py                # Package root; re-exports test suites for discovery
├── base.py                    # BaseAPITestCase fixture setup and assertion helpers
├── test_warehouse_api.py      # Warehouse CRUD, listing, and constraint tests
├── test_product_api.py        # Product CRUD, query filtering, and search tests
├── test_stock_adjustment.py   # Stock adjustment actions, limits, and state machine tests
├── test_auth.py               # Authentication endpoints (register, login, me)
└── test_concurrency.py        # Multi-threaded race condition tests on PostgreSQL
```

## Base Test Pattern: `BaseAPITestCase`

All API test classes should inherit from `BaseAPITestCase` defined in `warehouse/tests/base.py`:

```python
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from warehouse.models import Warehouse, Product, StockStatus


class BaseAPITestCase(APITestCase):
    def setUp(self):
        # Create standard test user and authentication token
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com'
        )
        self.token = Token.objects.create(user=self.user)

        # Authenticate test client by default
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Create baseline test warehouse
        self.warehouse = Warehouse.objects.create(
            name='Kho Test 01',
            code='KHO-TEST-01',
            location='Khu Cong Nghiep Hoa Lac',
            capacity=100
        )
```

## Mandatory Test Coverage Matrix

Every pull request or feature addition must maintain tests covering all relevant points of the matrix:

- **200 OK**: Retrieve details, retrieve filtered lists, update resource, execute stock adjustment.
- **201 Created**: Create warehouse, create product, register new user.
- **204 No Content**: Delete warehouse, delete product.
- **400 Bad Request**: Negative quantities, export exceeding available stock, import exceeding warehouse capacity, duplicate SKU/code.
- **401 Unauthorized**: Calling write endpoints without an Authorization token header.
- **404 Not Found**: Querying or modifying a non-existent warehouse or product ID.
- **State Machine Transitions**:
  - `quantity == 0` verifies `StockStatus.OUT_OF_STOCK`
  - `0 < quantity <= 10` verifies `StockStatus.LOW_STOCK`
  - `quantity > 10` verifies `StockStatus.IN_STOCK`

## Test Execution Commands

```powershell
# Run the entire test suite (72 tests)
python manage.py test

# Run a specific modular test file
python manage.py test warehouse.tests.test_warehouse_api
python manage.py test warehouse.tests.test_product_api
python manage.py test warehouse.tests.test_stock_adjustment
python manage.py test warehouse.tests.test_auth
python manage.py test warehouse.tests.test_concurrency
```

## Test Matrix and Code Recipes Reference

For complete test case specifications by endpoint, assertion recipes, and fixture setups, see [Test Matrix and Recipes Reference](references/test-matrix-and-recipes.md).
