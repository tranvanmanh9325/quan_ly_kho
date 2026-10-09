from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from warehouse.models import Warehouse, Product


class BaseWarehouseTestCase(APITestCase):
    """
    Base test case class providing authentication credentials
    and initial sample warehouse/product objects.
    """
    def setUp(self):
        super().setUp()
        # Create test user and token
        self.user = User.objects.create_user(
            username='teststaff',
            password='Password123@',
            email='teststaff@example.com',
            first_name='Test',
            last_name='Staff'
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
