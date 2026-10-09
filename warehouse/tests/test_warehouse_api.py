from decimal import Decimal
from rest_framework import status
from warehouse.models import Warehouse, Product
from .base import BaseWarehouseTestCase


class WarehouseAPITestCase(BaseWarehouseTestCase):
    """
    Test suite for Warehouse CRUD operations and custom actions.
    """

    def test_list_warehouses_200(self):
        # Verify listing warehouses returns HTTP 200 OK and list format
        response = self.client.get('/api/v1/warehouses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data or isinstance(response.data, list))

    def test_create_warehouse_201(self):
        # Verify creating warehouse returns HTTP 201 Created
        payload = {
            "name": "Kho Cần Thơ",
            "code": "KHO-CT-01",
            "location": "Ninh Kiều, Cần Thơ",
            "capacity": 2000
        }
        response = self.client.post('/api/v1/warehouses/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], "KHO-CT-01")

    def test_get_warehouse_detail_200(self):
        # Verify retrieving existing warehouse returns HTTP 200 OK
        response = self.client.get(f'/api/v1/warehouses/{self.warehouse.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.warehouse.id)

    def test_get_warehouse_not_found_404(self):
        # Verify retrieving non-existent warehouse returns HTTP 404 Not Found
        response = self.client.get('/api/v1/warehouses/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_warehouse_200(self):
        # Verify updating warehouse details returns HTTP 200 OK
        payload = {
            "name": "Kho Đà Nẵng Mở Rộng",
            "code": self.warehouse.code,
            "location": "Liên Chiểu, Đà Nẵng",
            "capacity": 500
        }
        response = self.client.put(f'/api/v1/warehouses/{self.warehouse.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.name, "Kho Đà Nẵng Mở Rộng")

    def test_delete_warehouse_204(self):
        # Verify deleting warehouse returns HTTP 204 No Content
        target_warehouse = Warehouse.objects.create(
            name="Kho Xóa",
            code="KHO-XOA-01",
            location="Địa chỉ tạm",
            capacity=100
        )
        response = self.client.delete(f'/api/v1/warehouses/{target_warehouse.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Warehouse.objects.filter(id=target_warehouse.id).exists())

    def test_get_warehouse_products_200(self):
        # Verify custom action fetching products of warehouse returns HTTP 200 OK
        response = self.client.get(f'/api/v1/warehouses/{self.warehouse.id}/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sku'], self.product.sku)

    def test_unauthenticated_user_cannot_create_warehouse_401(self):
        # Clear credentials to test authentication requirement
        self.client.credentials()
        payload = {
            "name": "Kho Lậu",
            "code": "KHO-LAU",
            "location": "Unknown",
            "capacity": 100
        }
        response = self.client.post('/api/v1/warehouses/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_update_warehouse_401(self):
        self.client.credentials()
        payload = {
            "name": "Kho Sửa Không Quyền",
            "code": self.warehouse.code,
            "location": "Hà Nội",
            "capacity": 500
        }
        response = self.client.put(f'/api/v1/warehouses/{self.warehouse.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_patch_warehouse_401(self):
        self.client.credentials()
        response = self.client.patch(f'/api/v1/warehouses/{self.warehouse.id}/', {"capacity": 300})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_warehouse_401(self):
        self.client.credentials()
        response = self.client.delete(f'/api/v1/warehouses/{self.warehouse.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_warehouse_not_found_404(self):
        payload = {
            "name": "Kho Không Tồn Tại",
            "code": "KHO-NONE",
            "location": "Hà Nội",
            "capacity": 500
        }
        response = self.client.put('/api/v1/warehouses/999999/', payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_warehouse_not_found_404(self):
        response = self.client.patch('/api/v1/warehouses/999999/', {"capacity": 500})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_warehouse_products_not_found_404(self):
        response = self.client.get('/api/v1/warehouses/999999/products/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_warehouse_success_200(self):
        response = self.client.patch(f'/api/v1/warehouses/{self.warehouse.id}/', {"capacity": 350})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.capacity, 350)

    def test_update_warehouse_capacity_below_current_stock_400(self):
        # Current stock in warehouse is self.product.quantity = 15. Attempting to reduce capacity to 10 (< 15) must fail.
        payload = {
            "name": self.warehouse.name,
            "code": self.warehouse.code,
            "location": self.warehouse.location,
            "capacity": 10
        }
        response = self.client.put(f'/api/v1/warehouses/{self.warehouse.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("capacity", response.data)

    def test_patch_warehouse_capacity_below_current_stock_400(self):
        # Patching capacity to 5 (< 15) must be rejected with HTTP 400 Bad Request
        response = self.client.patch(f'/api/v1/warehouses/{self.warehouse.id}/', {"capacity": 5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("capacity", response.data)

    def test_list_warehouses_query_count_is_constant(self):
        # Create 5 additional warehouses, each containing multiple products
        for i in range(5):
            wh = Warehouse.objects.create(
                name=f"Kho Benchmark {i}",
                code=f"KHO-BM-{i}",
                location="Hà Nội",
                capacity=1000
            )
            Product.objects.create(
                warehouse=wh,
                sku=f"SKU-BM-{i}-1",
                name=f"Hàng BM {i}-1",
                category="Benchmark",
                quantity=10,
                price=Decimal("100000.00")
            )
            Product.objects.create(
                warehouse=wh,
                sku=f"SKU-BM-{i}-2",
                name=f"Hàng BM {i}-2",
                category="Benchmark",
                quantity=20,
                price=Decimal("200000.00")
            )

        # Unauthenticate to measure pure endpoint query count without DRF token lookup overhead:
        # Expected queries:
        # 1 query for PageNumberPagination total count
        # 1 query for annotated warehouses list with aggregated Sum and Count
        # Total queries must be exactly 2, regardless of how many warehouses or products exist (O(1))
        self.client.credentials()
        with self.assertNumQueries(2):
            response = self.client.get('/api/v1/warehouses/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Confirm data correctness from annotations
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertGreaterEqual(len(results), 6)
        first_wh = next(item for item in results if item['code'] == self.warehouse.code)
        self.assertEqual(first_wh['current_total_quantity'], 15)
        self.assertEqual(first_wh['products_count'], 1)

    def test_get_warehouse_products_paginated_200(self):
        # Test pagination query parameter on /api/v1/warehouses/{id}/products/?page=1
        response = self.client.get(f'/api/v1/warehouses/{self.warehouse.id}/products/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

