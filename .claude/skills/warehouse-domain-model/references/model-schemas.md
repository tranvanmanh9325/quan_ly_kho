# Warehouse and Product Model Schemas Reference

This reference document provides database schema definitions, PostgreSQL constraints, ORM field configurations, and query optimization patterns for `Warehouse` and `Product` models.

## PostgreSQL Table Definitions

### Table `warehouse_warehouse`

```sql
CREATE TABLE warehouse_warehouse (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(255) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 1),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX warehouse_warehouse_code_idx ON warehouse_warehouse (code);
```

### Table `warehouse_product`

```sql
CREATE TABLE warehouse_product (
    id BIGSERIAL PRIMARY KEY,
    warehouse_id BIGINT NOT NULL REFERENCES warehouse_warehouse(id) ON DELETE CASCADE,
    sku VARCHAR(60) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0.00),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX warehouse_product_warehouse_id_idx ON warehouse_product (warehouse_id);
CREATE INDEX warehouse_product_sku_idx ON warehouse_product (sku);
CREATE INDEX warehouse_product_category_idx ON warehouse_product (category);
CREATE INDEX warehouse_product_status_idx ON warehouse_product (status);
```

## Django ORM Model Declarations

### Warehouse Model Source Code

```python
from django.db import models
from django.core.validators import MinValueValidator


class Warehouse(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Tên kho"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã kho"
    )
    location = models.CharField(
        max_length=255,
        verbose_name="Địa điểm"
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Sức chứa tối đa (đơn vị sản phẩm)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Kho hàng"
        verbose_name_plural = "Kho hàng"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def current_total_quantity(self):
        total = self.products.aggregate(
            total=models.Sum('quantity')
        )['total']
        return total or 0
```

### Product Model Source Code

```python
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .warehouse import Warehouse


class StockStatus(models.TextChoices):
    IN_STOCK = 'IN_STOCK', 'Còn hàng'
    LOW_STOCK = 'LOW_STOCK', 'Sắp hết hàng'
    OUT_OF_STOCK = 'OUT_OF_STOCK', 'Hết hàng'


class Product(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Thuộc kho"
    )
    sku = models.CharField(
        max_length=60,
        unique=True,
        verbose_name="Mã SKU"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Tên sản phẩm"
    )
    category = models.CharField(
        max_length=100,
        verbose_name="Danh mục"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Số lượng tồn kho"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Đơn giá (VNĐ)"
    )
    status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.OUT_OF_STOCK,
        verbose_name="Trạng thái tồn kho"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def clean(self):
        super().clean()
        if self.warehouse_id and self.quantity is not None:
            other_products = Product.objects.filter(warehouse=self.warehouse)
            if self.pk:
                other_products = other_products.exclude(pk=self.pk)
            current_used = other_products.aggregate(
                total=models.Sum('quantity')
            )['total'] or 0

            if current_used + self.quantity > self.warehouse.capacity:
                raise ValidationError(
                    f"Sức chứa kho không đủ! Sức chứa: {self.warehouse.capacity}, "
                    f"đang dùng: {current_used}, muốn thêm: {self.quantity}"
                )

    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.status = StockStatus.OUT_OF_STOCK
        elif self.quantity <= 10:
            self.status = StockStatus.LOW_STOCK
        else:
            self.status = StockStatus.IN_STOCK

        self.full_clean()
        super().save(*args, **kwargs)
```
