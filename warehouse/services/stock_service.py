from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from warehouse.models import Product, Warehouse


class InsufficientStockError(ValidationError):
    """Raised when attempting to export more quantity than currently available in stock."""
    def __init__(self, message: str):
        super().__init__({"error": message})


class StockCapacityError(ValidationError):
    """Raised when stock adjustment violates warehouse capacity constraints."""
    def __init__(self, message):
        if isinstance(message, dict) and 'quantity' in message:
            detail = message['quantity'][0] if isinstance(message['quantity'], list) else str(message['quantity'])
        elif isinstance(message, (list, tuple)):
            detail = message[0]
        else:
            detail = str(message)
        super().__init__({"error": detail})


@transaction.atomic
def adjust_product_stock(product: Product, adjustment_type: str, quantity: int) -> Product:
    """
    Adjusts the stock quantity of a given product (IMPORT or EXPORT) with strict concurrency safety.

    Enforces hierarchical locking:
    1. Lock parent Warehouse first to serialize operations on the warehouse.
    2. Lock child Product row to prevent stale in-memory reads and race conditions.

    Args:
        product: The Product model instance to be updated.
        adjustment_type: Action type ('IMPORT' or 'EXPORT').
        quantity: The quantity to add or subtract.

    Returns:
        Product: The updated and saved Product instance.

    Raises:
        InsufficientStockError: If exporting more than the current stock.
        StockCapacityError: If importing exceeds warehouse capacity.
        ValidationError: If the adjustment_type is invalid.
    """
    # 1. Lock parent Warehouse to protect capacity invariant across concurrent imports
    Warehouse.objects.select_for_update().get(pk=product.warehouse_id)

    # 2. Lock child Product to fetch freshest quantity and prevent lost updates
    product = Product.objects.select_for_update().get(pk=product.pk)

    if adjustment_type == 'EXPORT':
        if product.quantity < quantity:
            raise InsufficientStockError(
                f"Số lượng tồn kho không đủ để xuất! Hiện tại chỉ còn {product.quantity}, yêu cầu xuất {quantity}."
            )
        product.quantity -= quantity
    elif adjustment_type == 'IMPORT':
        product.quantity += quantity
    else:
        raise ValidationError({
            "error": f"Hành động không hợp lệ: {adjustment_type}."
        })

    try:
        product.save()
    except DjangoValidationError as exc:
        message = exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
        raise StockCapacityError(message)

    return product
