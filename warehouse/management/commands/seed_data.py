from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from warehouse.models import Warehouse, Product
from decimal import Decimal


class Command(BaseCommand):
    help = "Seed initial sample data for warehouse management system"

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data...")

        # Create or update demo staff user
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@kho.local",
                "is_staff": True,
                "is_superuser": True
            }
        )
        user.set_password("AdminPassword123@")
        user.save()
        token, _ = Token.objects.get_or_create(user=user)

        self.stdout.write(self.style.SUCCESS(f"User: admin / AdminPassword123@ (Token: {token.key})"))

        # Create Warehouses
        kho_hn, _ = Warehouse.objects.get_or_create(
            code="KHO-HN-01",
            defaults={
                "name": "Kho Tổng Hà Nội",
                "location": "Số 12 Khu Công Nghiệp Thăng Long, Đông Anh, Hà Nội",
                "capacity": 5000,
                "is_active": True
            }
        )

        kho_hcm, _ = Warehouse.objects.get_or_create(
            code="KHO-HCM-01",
            defaults={
                "name": "Kho Phía Nam - TP.HCM",
                "location": "Lô B2 Đường Tân Thuận, KCX Tân Thuận, Quận 7, TP.HCM",
                "capacity": 8000,
                "is_active": True
            }
        )

        # Create Products
        products_data = [
            {
                "warehouse": kho_hn,
                "sku": "SKU-DELL-XPS15",
                "name": "Laptop Dell XPS 15 9530",
                "category": "Máy tính & Laptop",
                "quantity": 50,
                "price": Decimal("38500000.00")
            },
            {
                "warehouse": kho_hn,
                "sku": "SKU-LG-27UP850",
                "name": "Màn hình LG 27 inch 4K UHD",
                "category": "Màn hình máy tính",
                "quantity": 8, # Should trigger LOW_STOCK
                "price": Decimal("8900000.00")
            },
            {
                "warehouse": kho_hn,
                "sku": "SKU-KEYCHRON-Q1",
                "name": "Bàn phím cơ Keychron Q1 Pro",
                "category": "Phụ kiện",
                "quantity": 0, # Should trigger OUT_OF_STOCK
                "price": Decimal("4200000.00")
            },
            {
                "warehouse": kho_hcm,
                "sku": "SKU-LOGI-MX3S",
                "name": "Chuột không dây Logitech MX Master 3S",
                "category": "Phụ kiện",
                "quantity": 120,
                "price": Decimal("2450000.00")
            },
            {
                "warehouse": kho_hcm,
                "sku": "SKU-IPHONE-16PM",
                "name": "Điện thoại Apple iPhone 16 Pro Max 256GB",
                "category": "Điện thoại",
                "quantity": 25,
                "price": Decimal("34990000.00")
            }
        ]

        for p_data in products_data:
            product, p_created = Product.objects.get_or_create(
                sku=p_data["sku"],
                defaults=p_data
            )
            if not p_created:
                for k, v in p_data.items():
                    setattr(product, k, v)
                product.save()

        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully!"))
