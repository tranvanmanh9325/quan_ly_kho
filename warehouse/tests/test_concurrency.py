from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.db import connection
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

from warehouse.models import Warehouse, Product
from warehouse.services import (
    adjust_product_stock,
    InsufficientStockError,
    StockCapacityError
)


class StockConcurrencyTestCase(TransactionTestCase):
    """
    Real PostgreSQL Concurrency Test Suite.
    Uses TransactionTestCase so that database changes are committed to the
    real PostgreSQL database, allowing multiple concurrent worker threads
    with independent database connections to test row-level locking (select_for_update)
    and race-condition prevention under realistic production conditions.
    """

    def setUp(self):
        super().setUp()
        # Clean up any leftover records to ensure idempotent test runs
        Product.objects.all().delete()
        Warehouse.objects.all().delete()
        User.objects.all().delete()

        # Create test user and auth token for API-level concurrency tests
        self.user = User.objects.create_user(
            username='concurrency_staff',
            password='StrongPass123@',
            email='concurrency@example.com'
        )
        self.token = Token.objects.create(user=self.user)

    def tearDown(self):
        # Ensure thread connections are cleaned up
        connection.close()
        super().tearDown()

    def test_concurrent_export_prevents_negative_stock(self):
        """
        Scenario 1: Concurrent Export Race Condition (Anti-underflow verification).
        Initial stock: 15 items.
        10 concurrent threads each attempt to export 2 items.
        Total requested export = 20 items > available 15 items.

        Assertion:
        - Exactly 7 operations succeed (7 * 2 = 14 items exported).
        - Exactly 3 operations fail with InsufficientStockError.
        - Final stock quantity is exactly 1 (15 - 14 = 1).
        - Stock never drops below zero under any race condition.
        """
        warehouse = Warehouse.objects.create(
            name="Kho Concurrency Export",
            code="KHO-CC-EXP-01",
            location="Đà Nẵng",
            capacity=1000
        )
        product = Product.objects.create(
            warehouse=warehouse,
            sku="SKU-CC-EXP-001",
            name="Sản phẩm Test Export Concurrency",
            category="Concurrency",
            quantity=15,
            price=Decimal("100000.00")
        )

        def worker_export(product_id, export_qty):
            from django.db import connection
            try:
                prod = Product.objects.get(pk=product_id)
                adjust_product_stock(prod, 'EXPORT', export_qty)
                return True, None
            except InsufficientStockError as exc:
                return False, exc
            finally:
                connection.close()

        num_threads = 10
        export_qty = 2
        successes = 0
        failures = 0

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(worker_export, product.id, export_qty)
                for _ in range(num_threads)
            ]
            for future in as_completed(futures):
                success, exc = future.result()
                if success:
                    successes += 1
                else:
                    failures += 1
                    self.assertIsInstance(exc, InsufficientStockError)

        product.refresh_from_db()
        self.assertEqual(successes, 7, f"Expected 7 successful exports, got {successes}")
        self.assertEqual(failures, 3, f"Expected 3 rejected exports, got {failures}")
        self.assertEqual(product.quantity, 1, f"Expected remaining stock 1, got {product.quantity}")
        self.assertGreaterEqual(product.quantity, 0, "Inventory must never be negative!")
        self.assertEqual(product.status, "LOW_STOCK")

    def test_concurrent_import_prevents_capacity_overflow(self):
        """
        Scenario 2: Concurrent Import Race Condition (Anti-capacity overflow verification).
        Initial warehouse capacity: 100 items.
        Two products exist in the warehouse:
        - Product A: 40 items
        - Product B: 40 items
        Current warehouse total = 80 items. Remaining capacity = 20 items.

        6 concurrent threads each attempt to import 10 items (threads alternate between A and B).
        Total requested import = 6 * 10 = 60 items > remaining capacity 20 items.

        Assertion:
        - Exactly 2 operations succeed (2 * 10 = 20 items imported, filling the warehouse).
        - Exactly 4 operations fail with StockCapacityError.
        - Final total stock in warehouse is exactly 100 items.
        - Warehouse capacity is strictly never breached.
        """
        warehouse = Warehouse.objects.create(
            name="Kho Concurrency Import",
            code="KHO-CC-IMP-01",
            location="Hà Nội",
            capacity=100
        )
        prod_a = Product.objects.create(
            warehouse=warehouse,
            sku="SKU-CC-IMP-A",
            name="Sản phẩm A",
            category="Concurrency",
            quantity=40,
            price=Decimal("50000.00")
        )
        prod_b = Product.objects.create(
            warehouse=warehouse,
            sku="SKU-CC-IMP-B",
            name="Sản phẩm B",
            category="Concurrency",
            quantity=40,
            price=Decimal("50000.00")
        )

        def worker_import(product_id, import_qty):
            from django.db import connection
            try:
                prod = Product.objects.get(pk=product_id)
                adjust_product_stock(prod, 'IMPORT', import_qty)
                return True, None
            except StockCapacityError as exc:
                return False, exc
            finally:
                connection.close()

        num_threads = 6
        import_qty = 10
        successes = 0
        failures = 0

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(
                    worker_import,
                    prod_a.id if i % 2 == 0 else prod_b.id,
                    import_qty
                )
                for i in range(num_threads)
            ]
            for future in as_completed(futures):
                success, exc = future.result()
                if success:
                    successes += 1
                else:
                    failures += 1
                    self.assertIsInstance(exc, StockCapacityError)

        warehouse.refresh_from_db()
        prod_a.refresh_from_db()
        prod_b.refresh_from_db()

        self.assertEqual(successes, 2, f"Expected 2 successful imports, got {successes}")
        self.assertEqual(failures, 4, f"Expected 4 rejected imports, got {failures}")
        self.assertEqual(
            warehouse.current_total_quantity, 100,
            f"Expected warehouse stock to equal capacity (100), got {warehouse.current_total_quantity}"
        )
        self.assertLessEqual(
            warehouse.current_total_quantity, warehouse.capacity,
            "Warehouse capacity must never be exceeded!"
        )

    def test_concurrent_api_adjust_stock_endpoints(self):
        """
        Scenario 3: Concurrent End-to-End API Requests.
        10 concurrent threads call POST /api/v1/products/{id}/adjust-stock/
        via distinct APIClient instances with Token Authentication.
        Product initial quantity: 25.
        Each thread requests to EXPORT 3 items. Total = 30 > 25.

        Assertion:
        - Exactly 8 HTTP 200 OK responses (8 * 3 = 24 items).
        - Exactly 2 HTTP 400 Bad Request responses.
        - Database state is consistent: final quantity = 1.
        """
        warehouse = Warehouse.objects.create(
            name="Kho Concurrency API",
            code="KHO-CC-API-01",
            location="TP.HCM",
            capacity=500
        )
        product = Product.objects.create(
            warehouse=warehouse,
            sku="SKU-CC-API-001",
            name="Sản phẩm Test API Concurrency",
            category="API",
            quantity=25,
            price=Decimal("200000.00")
        )

        token_key = self.token.key

        def worker_api_call(product_id, export_qty):
            from django.db import connection
            try:
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION=f'Token {token_key}')
                response = client.post(
                    f'/api/v1/products/{product_id}/adjust-stock/',
                    {"action": "EXPORT", "quantity": export_qty},
                    format='json'
                )
                return response.status_code, response.data
            finally:
                connection.close()

        num_threads = 10
        export_qty = 3
        status_200_count = 0
        status_400_count = 0

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(worker_api_call, product.id, export_qty)
                for _ in range(num_threads)
            ]
            for future in as_completed(futures):
                code, data = future.result()
                if code == status.HTTP_200_OK:
                    status_200_count += 1
                elif code == status.HTTP_400_BAD_REQUEST:
                    status_400_count += 1
                    self.assertIn("error", data)

        product.refresh_from_db()
        self.assertEqual(status_200_count, 8, f"Expected 8 HTTP 200 OK, got {status_200_count}")
        self.assertEqual(status_400_count, 2, f"Expected 2 HTTP 400 Bad Request, got {status_400_count}")
        self.assertEqual(product.quantity, 1, f"Expected remaining quantity 1, got {product.quantity}")

    def test_deadlock_free_repeated_concurrent_operations(self):
        """
        Scenario 4: Deadlock-Free Verification across 5 repeated concurrent cycles.
        Repeatedly executes mixed concurrent operations (both IMPORT and EXPORT)
        across multiple threads on the same warehouse and products.
        Verifies that PostgreSQL error 40P01 (deadlock detected) never occurs.
        """
        for iteration in range(1, 6):
            wh = Warehouse.objects.create(
                name=f"Kho Deadlock Test {iteration}",
                code=f"KHO-DL-{iteration}",
                location="Hải Phòng",
                capacity=500
            )
            p1 = Product.objects.create(
                warehouse=wh,
                sku=f"SKU-DL-1-{iteration}",
                name="Sản phẩm DL 1",
                category="Deadlock",
                quantity=50,
                price=Decimal("10000.00")
            )
            p2 = Product.objects.create(
                warehouse=wh,
                sku=f"SKU-DL-2-{iteration}",
                name="Sản phẩm DL 2",
                category="Deadlock",
                quantity=50,
                price=Decimal("20000.00")
            )

            def worker_mixed_action(prod_id, action, qty):
                from django.db import connection
                try:
                    prod = Product.objects.get(pk=prod_id)
                    adjust_product_stock(prod, action, qty)
                    return True, None
                except (InsufficientStockError, StockCapacityError) as exc:
                    return False, exc
                finally:
                    connection.close()

            # Launch 8 interleaved threads (4 import, 4 export)
            with ThreadPoolExecutor(max_workers=8) as executor:
                tasks = []
                for i in range(8):
                    target_prod_id = p1.id if i % 2 == 0 else p2.id
                    action = 'IMPORT' if i < 4 else 'EXPORT'
                    tasks.append(executor.submit(worker_mixed_action, target_prod_id, action, 5))

                for future in as_completed(tasks):
                    # Will re-raise if OperationalError (deadlock) occurred
                    future.result()

            # Refresh and verify invariants
            wh.refresh_from_db()
            p1.refresh_from_db()
            p2.refresh_from_db()
            self.assertGreaterEqual(p1.quantity, 0)
            self.assertGreaterEqual(p2.quantity, 0)
            self.assertLessEqual(wh.current_total_quantity, wh.capacity)
