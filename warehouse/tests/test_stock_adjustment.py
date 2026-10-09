from rest_framework import status
from .base import BaseWarehouseTestCase


class StockAdjustmentAPITestCase(BaseWarehouseTestCase):
    """
    Test suite for Stock Adjustment API (IMPORT, EXPORT, constraints, validations).
    """

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
        # Verify exporting stock decreases quantity and updates status
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
        self.assertIn("không đủ để xuất", response.data['error'])
        self.assertNotIn('message', response.data)

    def test_stock_adjustment_invalid_action_400(self):
        # Verify invalid action type is rejected with HTTP 400 Bad Request
        payload = {
            "action": "TRANSFER",
            "quantity": 5
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_adjustment_non_positive_quantity_400(self):
        # Verify zero or negative quantity is rejected with HTTP 400 Bad Request
        payload = {
            "action": "IMPORT",
            "quantity": 0
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_adjustment_import_exceeds_capacity_400(self):
        # Warehouse capacity is 100, current quantity is 15. Importing 90 causes total = 105 > 100.
        payload = {
            "action": "IMPORT",
            "quantity": 90,
            "note": "Nhập quá tải"
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vượt quá sức chứa", str(response.data['error']))
        self.assertNotIn('message', response.data)

    def test_unauthenticated_user_cannot_adjust_stock_401(self):
        self.client.credentials()
        payload = {
            "action": "IMPORT",
            "quantity": 5
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_adjust_stock_product_not_found_404(self):
        payload = {
            "action": "IMPORT",
            "quantity": 5
        }
        response = self.client.post('/api/v1/products/999999/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stock_adjustment_negative_quantity_400(self):
        payload = {
            "action": "IMPORT",
            "quantity": -5
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_stock_transition_to_out_of_stock_when_zero(self):
        # Current quantity is 15 (IN_STOCK). Export exactly 15 items -> quantity becomes 0, status transitions to OUT_OF_STOCK
        payload = {
            "action": "EXPORT",
            "quantity": 15
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 0)
        self.assertEqual(self.product.status, 'OUT_OF_STOCK')

    def test_stock_transition_from_out_of_stock_to_low_stock(self):
        # Set quantity to 0 (OUT_OF_STOCK) first
        self.product.quantity = 0
        self.product.save()
        self.assertEqual(self.product.status, 'OUT_OF_STOCK')

        # Import 5 items (1 <= qty <= 10) -> status must transition to LOW_STOCK
        payload = {
            "action": "IMPORT",
            "quantity": 5
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 5)
        self.assertEqual(self.product.status, 'LOW_STOCK')

    def test_stock_transition_from_low_stock_to_in_stock(self):
        # Set quantity to 5 (LOW_STOCK)
        self.product.quantity = 5
        self.product.save()
        self.assertEqual(self.product.status, 'LOW_STOCK')

        # Import 10 items -> total is 15 (> 10) -> status transitions to IN_STOCK
        payload = {
            "action": "IMPORT",
            "quantity": 10
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15)
        self.assertEqual(self.product.status, 'IN_STOCK')

    def test_stock_transition_from_in_stock_to_out_of_stock_directly(self):
        # Starting with 15 (IN_STOCK), export all 15 directly
        payload = {
            "action": "EXPORT",
            "quantity": 15
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 0)
        self.assertEqual(self.product.status, 'OUT_OF_STOCK')

    def test_stock_transition_from_out_of_stock_to_in_stock_directly(self):
        # Starting from 0 (OUT_OF_STOCK), import 25 items directly (> 10) -> status is IN_STOCK
        self.product.quantity = 0
        self.product.save()

        payload = {
            "action": "IMPORT",
            "quantity": 25
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 25)
        self.assertEqual(self.product.status, 'IN_STOCK')

    def test_error_format_non_field_domain_error(self):
        # Exporting more than available stock should return unified non-field format {"error": "..."}
        payload = {
            "action": "EXPORT",
            "quantity": 999
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIsInstance(response.data["error"], str)
        self.assertNotIn("BAD_REQUEST", response.data)
        self.assertNotIn("message", response.data)

    def test_error_format_field_validation_error(self):
        # Invalid field input should return unified field validation format {"field": ["..."]}
        payload = {
            "action": "IMPORT",
            "quantity": 0
        }
        response = self.client.post(f'/api/v1/products/{self.product.id}/adjust-stock/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertIsInstance(response.data["quantity"], list)

