from decimal import Decimal
from rest_framework import status
from warehouse.models import Product, Warehouse
from .base import BaseWarehouseTestCase


class ProductAPITestCase(BaseWarehouseTestCase):
    """
    Test suite for Product CRUD operations, validations, and query filters.
    """

    def test_create_product_201(self):
        # Verify creating valid product returns HTTP 201 Created
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-NEW-002",
            "name": "Tai nghe bluetooth",
            "category": "Phụ kiện",
            "quantity": 20,
            "price": "350000.00"
        }
        response = self.client.post('/api/v1/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'IN_STOCK')

    def test_create_product_invalid_quantity_400(self):
        # Verify creating product with negative quantity returns HTTP 400 Bad Request
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-INVALID-QTY",
            "name": "Sản phẩm lỗi",
            "category": "Lỗi",
            "quantity": -5,
            "price": "100000.00"
        }
        response = self.client.post('/api/v1/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_invalid_price_400(self):
        # Verify creating product with negative price returns HTTP 400 Bad Request
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-INVALID-PRICE",
            "name": "Sản phẩm giá âm",
            "category": "Lỗi",
            "quantity": 10,
            "price": "-50000.00"
        }
        response = self.client.post('/api/v1/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_exceeds_warehouse_capacity_400(self):
        # Verify creating product exceeding warehouse capacity returns HTTP 400 Bad Request
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-OVERFLOW",
            "name": "Hàng quá tải",
            "category": "Nặng",
            "quantity": 200,  # Warehouse capacity is 100, current quantity is 15
            "price": "100000.00"
        }
        response = self.client.post('/api/v1/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_product_detail_200(self):
        # Verify retrieving existing product detail returns HTTP 200 OK
        response = self.client.get(f'/api/v1/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sku'], self.product.sku)

    def test_get_product_not_found_404(self):
        # Verify retrieving non-existent product returns HTTP 404 Not Found
        response = self.client.get('/api/v1/products/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_204(self):
        # Verify deleting product returns HTTP 204 No Content
        response = self.client.delete(f'/api/v1/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_filter_products_by_warehouse_200(self):
        # Create second warehouse and product to verify filtering
        wh2 = Warehouse.objects.create(name="Kho Phụ", code="KHO-PHU-01", location="Huế", capacity=500)
        Product.objects.create(
            warehouse=wh2,
            sku="SKU-PHU-001",
            name="Sản phẩm kho phụ",
            category="Khác",
            quantity=5,
            price=Decimal("50000.00")
        )

        response = self.client.get(f'/api/v1/products/?warehouse={self.warehouse.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(all(item['warehouse'] == self.warehouse.id for item in results))

    def test_filter_products_by_category_200(self):
        response = self.client.get('/api/v1/products/?category=Kiểm thử')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(all(item['category'].lower() == 'kiểm thử' for item in results))

    def test_filter_products_by_status_200(self):
        response = self.client.get('/api/v1/products/?status=IN_STOCK')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(all(item['status'] == 'IN_STOCK' for item in results))

    def test_search_products_by_name_or_sku_200(self):
        response = self.client.get('/api/v1/products/?search=SKU-TEST')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)

    def test_unauthenticated_user_cannot_create_product_401(self):
        self.client.credentials()
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-UNAUTH-01",
            "name": "Sp không quyền",
            "category": "Test",
            "quantity": 10,
            "price": "100000.00"
        }
        response = self.client.post('/api/v1/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_update_product_401(self):
        self.client.credentials()
        payload = {
            "warehouse": self.warehouse.id,
            "sku": self.product.sku,
            "name": "Sp sửa không quyền",
            "category": "Test",
            "quantity": 10,
            "price": "100000.00"
        }
        response = self.client.put(f'/api/v1/products/{self.product.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_patch_product_401(self):
        self.client.credentials()
        response = self.client.patch(f'/api/v1/products/{self.product.id}/', {"name": "Patch không quyền"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_product_401(self):
        self.client.credentials()
        response = self.client.delete(f'/api/v1/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_not_found_404(self):
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-NOT-EXIST",
            "name": "Sp không tồn tại",
            "category": "Test",
            "quantity": 10,
            "price": "100000.00"
        }
        response = self.client.put('/api/v1/products/999999/', payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_product_not_found_404(self):
        response = self.client.patch('/api/v1/products/999999/', {"name": "Sp không tồn tại"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_success_200(self):
        # Happy Path: Update product details completely
        payload = {
            "warehouse": self.warehouse.id,
            "sku": self.product.sku,
            "name": "Sản phẩm đã cập nhật tên",
            "category": "Điện tử cao cấp",
            "quantity": 30,
            "price": "250000.00"
        }
        response = self.client.put(f'/api/v1/products/{self.product.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Sản phẩm đã cập nhật tên")
        self.assertEqual(self.product.category, "Điện tử cao cấp")
        self.assertEqual(self.product.quantity, 30)
        self.assertEqual(self.product.price, Decimal("250000.00"))
        self.assertEqual(self.product.status, "IN_STOCK")

    def test_patch_product_success_200(self):
        # Partial update with PATCH
        payload = {
            "name": "Tên sản phẩm sau PATCH",
            "price": "199000.00"
        }
        response = self.client.patch(f'/api/v1/products/{self.product.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Tên sản phẩm sau PATCH")
        self.assertEqual(self.product.price, Decimal("199000.00"))

    def test_update_product_negative_quantity_400(self):
        payload = {
            "warehouse": self.warehouse.id,
            "sku": self.product.sku,
            "name": self.product.name,
            "category": self.product.category,
            "quantity": -10,
            "price": "150000.00"
        }
        response = self.client.put(f'/api/v1/products/{self.product.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_update_product_negative_price_400(self):
        payload = {
            "warehouse": self.warehouse.id,
            "sku": self.product.sku,
            "name": self.product.name,
            "category": self.product.category,
            "quantity": self.product.quantity,
            "price": "-50000.00"
        }
        response = self.client.put(f'/api/v1/products/{self.product.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_update_product_exceeds_warehouse_capacity_400(self):
        # Warehouse capacity is 100, current product quantity is 15. Attempting to update quantity to 120 (> 100) must fail.
        payload = {
            "warehouse": self.warehouse.id,
            "sku": self.product.sku,
            "name": self.product.name,
            "category": self.product.category,
            "quantity": 120,
            "price": "150000.00"
        }
        response = self.client.put(f'/api/v1/products/{self.product.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_filter_products_combined_warehouse_and_status_200(self):
        # Create second product in same warehouse with LOW_STOCK status
        Product.objects.create(
            warehouse=self.warehouse,
            sku="SKU-TEST-LOW",
            name="Sản phẩm tồn thấp",
            category="Kiểm thử",
            quantity=5,
            price=Decimal("120000.00")
        )

        response = self.client.get(f'/api/v1/products/?warehouse={self.warehouse.id}&status=LOW_STOCK')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['sku'], "SKU-TEST-LOW")
        self.assertEqual(results[0]['status'], "LOW_STOCK")

