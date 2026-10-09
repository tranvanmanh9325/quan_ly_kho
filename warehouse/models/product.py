from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from .warehouse import Warehouse


class StockStatus(models.TextChoices):
    IN_STOCK = 'IN_STOCK', 'Còn hàng'
    LOW_STOCK = 'LOW_STOCK', 'Sắp hết hàng'
    OUT_OF_STOCK = 'OUT_OF_STOCK', 'Hết hàng'


class Product(models.Model):
    StockStatus = StockStatus

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Thuộc kho"
    )
    sku = models.CharField(max_length=60, unique=True, verbose_name="Mã SKU")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    category = models.CharField(max_length=100, verbose_name="Danh mục")
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Số lượng tồn kho"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Đơn giá"
    )
    status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.OUT_OF_STOCK,
        verbose_name="Trạng thái"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"

    def __str__(self):
        return f"{self.name} [{self.sku}]"

    def clean(self):
        super().clean()
        # Verify warehouse capacity is not exceeded when adding/updating stock
        if self.warehouse_id:
            current_other_total = (
                self.warehouse.products.exclude(pk=self.pk).aggregate(total=models.Sum('quantity'))['total'] or 0
            )
            if current_other_total + self.quantity > self.warehouse.capacity:
                raise ValidationError({
                    'quantity': f"Tổng số lượng ({current_other_total + self.quantity}) vượt quá sức chứa của kho ({self.warehouse.capacity})!"
                })

    def save(self, *args, **kwargs):
        # Keep status synchronized with quantity automatically
        if self.quantity == 0:
            self.status = self.StockStatus.OUT_OF_STOCK
        elif self.quantity <= 10:
            self.status = self.StockStatus.LOW_STOCK
        else:
            self.status = self.StockStatus.IN_STOCK

        self.full_clean()
        super().save(*args, **kwargs)
