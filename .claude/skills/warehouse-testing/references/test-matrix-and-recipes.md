# Test Matrix and Recipes Reference

This reference document catalogues the required test matrix across all 15 API endpoints and provides reusable test recipes for the Warehouse Management Backend.

## Complete API Test Matrix

| Endpoint | Method | Test Scenarios | Expected Status |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/register/` | POST | Valid user registration data | 201 Created |
| `/api/v1/auth/register/` | POST | Duplicate username or invalid email | 400 Bad Request |
| `/api/v1/auth/login/` | POST | Valid credentials | 200 OK |
| `/api/v1/auth/login/` | POST | Incorrect password or invalid user | 400 Bad Request |
| `/api/v1/auth/me/` | GET | Authenticated user with Token | 200 OK |
| `/api/v1/auth/me/` | GET | Unauthenticated request without Token | 401 Unauthorized |
| `/api/v1/warehouses/` | GET | Retrieve paginated warehouse list | 200 OK |
| `/api/v1/warehouses/` | POST | Create warehouse with valid data | 201 Created |
| `/api/v1/warehouses/` | POST | Missing Token authentication | 401 Unauthorized |
| `/api/v1/warehouses/{id}/` | GET | Existing warehouse ID | 200 OK |
| `/api/v1/warehouses/{id}/` | GET | Non-existent warehouse ID (e.g. 9999) | 404 Not Found |
| `/api/v1/warehouses/{id}/` | PUT | Valid update with Token | 200 OK |
| `/api/v1/warehouses/{id}/` | DELETE | Delete warehouse with Token | 204 No Content |
| `/api/v1/warehouses/{id}/products/` | GET | List products within specified warehouse | 200 OK |
| `/api/v1/products/` | GET | Retrieve products with query filters | 200 OK |
| `/api/v1/products/` | POST | Create product with valid data | 201 Created |
| `/api/v1/products/` | POST | Product quantity exceeds warehouse capacity | 400 Bad Request |
| `/api/v1/products/{id}/` | GET | Existing product ID | 200 OK |
| `/api/v1/products/{id}/` | GET | Non-existent product ID (e.g. 9999) | 404 Not Found |
| `/api/v1/products/{id}/` | PUT | Update product attributes | 200 OK |
| `/api/v1/products/{id}/` | DELETE | Delete product with Token | 204 No Content |
| `/api/v1/products/{id}/adjust-stock/` | POST | Valid IMPORT within capacity | 200 OK |
| `/api/v1/products/{id}/adjust-stock/` | POST | Valid EXPORT reducing stock to LOW_STOCK | 200 OK |
| `/api/v1/products/{id}/adjust-stock/` | POST | EXPORT quantity greater than stock balance | 400 Bad Request |
| `/api/v1/products/{id}/adjust-stock/` | POST | Negative or zero quantity value | 400 Bad Request |
| `/api/v1/products/{id}/adjust-stock/` | POST | Unauthenticated request | 401 Unauthorized |

## Test Implementation Recipes

### Recipe 1: Testing Stock Adjustment Validation

```python
from rest_framework import status
from warehouse.models import Product, StockStatus
from warehouse.tests.base import BaseAPITestCase


class TestStockAdjustmentAPI(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            warehouse=self.warehouse,
            sku='SKU-TEST-001',
            name='Test Item',
            category='Phu kien',
            quantity=20,
            price='100000.00'
        )

    def test_export_exceeding_stock_returns_400(self):
        url = f'/api/v1/products/{self.product.id}/adjust-stock/'
        payload = {'action': 'EXPORT', 'quantity': 25}
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

        # Confirm database state was not modified
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 20)
```

### Recipe 2: Testing Capacity Overflow on Creation

```python
from rest_framework import status
from warehouse.tests.base import BaseAPITestCase


class TestProductCapacityAPI(BaseAPITestCase):
    def test_product_creation_exceeding_capacity_returns_400(self):
        # Warehouse capacity is 100 in BaseAPITestCase
        url = '/api/v1/products/'
        payload = {
            'warehouse': self.warehouse.id,
            'sku': 'SKU-OVERFLOW-001',
            'name': 'Bulky Item',
            'category': 'Thiet bi',
            'quantity': 150,
            'price': '500000.00'
        }
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```
