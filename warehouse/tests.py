from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .models import Warehouse, Product


class WarehouseAPITestCase(APITestCase):
    def setUp(self):
        # Create test user and token
        self.user = User.objects.create_user(
            username='teststaff',
            password='Password123@'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create sample warehouse
        self.warehouse = Warehouse.objects.create(
            name="Kho Test Đà Nẵng",
            code="KHO-DN-01",
            location="Hòa Khánh, Đà Nẵng",
            capacity=100
        )

        # Create sample product
        self.product = Product.objects.create(
            warehouse=self.warehouse,
            sku="SKU-TEST-001",
            name="Sản phẩm kiểm thử",
            category="Kiểm thử",
            quantity=15,
            price=Decimal("150000.00")
        )

    def test_list_warehouses_200(self):
        # Verify listing warehouses returns HTTP 200 OK and JSON list
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

    def test_create_product_exceeds_warehouse_capacity_400(self):
        # Verify creating product exceeding warehouse capacity returns HTTP 400 Bad Request
        payload = {
            "warehouse": self.warehouse.id,
            "sku": "SKU-OVERFLOW",
            "name": "Hàng quá tải",
            "category": "Nặng",
            "quantity": 200, # Warehouse capacity is 100, current quantity is 15
            "price": "100000.00"
        }
        response = self.client.post('/api/v1/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_adjustment_import_200(self):
        # Verify importing stock increases quantity and returns HTTP 200 OK
        payload = {
            "action": "IMPORT",
            "quantity": 10,
            "note": "Nhập thêm hàng từ nhà cung cấp"
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 25)

    def test_stock_adjustment_export_success_200(self):
        # Verify exporting stock decreases quantity
        payload = {
            "action": "EXPORT",
            "quantity": 5,
            "note": "Xuất bán cho khách"
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.status, 'LOW_STOCK')

    def test_stock_adjustment_export_insufficient_400(self):
        # Verify exporting more than current stock returns HTTP 400 Bad Request
        payload = {
            "action": "EXPORT",
            "quantity": 999
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("không đủ để xuất", response.data['message'])

    def test_delete_product_204(self):
        # Verify deleting product returns HTTP 204 No Content
        response = self.client.delete(f'/api/v1/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

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
