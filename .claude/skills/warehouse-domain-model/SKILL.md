---
name: warehouse-domain-model
description: Use this skill when designing, querying, modifying, or validating Warehouse and Product domain models, entity relationships, database schema fields, capacity constraints, or stock status state machine transitions in the warehouse management system.
---

# Warehouse Domain Model Skill

This skill provides domain model specifications, schema invariants, business validation rules, and entity lifecycle behaviors for the Warehouse Management Backend.

## Domain Model Architecture

The domain models are partitioned per object under `warehouse/models/`:

- `warehouse/models/warehouse.py`: The `Warehouse` physical facility entity and capacity calculations.
- `warehouse/models/product.py`: The `Product` inventory item entity and `StockStatus` enumeration.
- `warehouse/models/__init__.py`: Re-exports `Warehouse`, `Product`, and `StockStatus` to preserve backwards compatibility.

## Entity Specifications

### Warehouse Entity

Represents a physical storage location with capacity limits:

- `id`: AutoField (Primary Key)
- `name`: `CharField(max_length=150)` — Facility name (e.g. "Kho Hà Nội 01")
- `code`: `CharField(max_length=50, unique=True)` — Unique facility identifier (e.g. `KHO-HN-01`)
- `location`: `CharField(max_length=255)` — Physical facility address
- `capacity`: `PositiveIntegerField` — Maximum total quantity of items this warehouse can store (minimum 1)
- `is_active`: `BooleanField(default=True)` — Operating status flag
- `current_total_quantity`: Dynamic property computing the aggregate sum of all associated product quantities:

```python
@property
def current_total_quantity(self):
    total = self.products.aggregate(models.Sum('quantity'))['quantity__sum']
    return total or 0
```

- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

### Product Entity

Represents physical stock units assigned to a specific warehouse:

- `id`: AutoField (Primary Key)
- `warehouse`: `ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='products')`
- `sku`: `CharField(max_length=60, unique=True)` — Stock Keeping Unit code (e.g. `SKU-DELL-XPS15`)
- `name`: `CharField(max_length=200)` — Product title
- `category`: `CharField(max_length=100)` — Classification category (e.g. "Laptop", "Phụ kiện")
- `quantity`: `PositiveIntegerField(default=0)` — Current inventory level
- `price`: `DecimalField(max_digits=12, decimal_places=2)` — Unit price in VND (minimum 0.00)
- `status`: `CharField(max_length=20, choices=StockStatus.choices)` — Auto-calculated inventory state
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

### StockStatus Enumeration

- `IN_STOCK`: Quantity greater than 10 units (`quantity > 10`)
- `LOW_STOCK`: Quantity between 1 and 10 units (`0 < quantity <= 10`)
- `OUT_OF_STOCK`: Quantity equals 0 (`quantity == 0`)

## Business Invariants and Lifecycle Rules

### Capacity Constraint Validation

The aggregate item count across all products in a warehouse must never exceed the facility's defined capacity:

$$\sum_{\text{other}} \text{quantity} + \text{current.quantity} \le \text{warehouse.capacity}$$

Validation is enforced in `Product.clean()`:

```python
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
```

### Automated State Machine Lifecycle

The `status` field is automatically derived in `Product.save()` prior to persistence:

```python
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

## Detailed Schemas and Queries Reference

For comprehensive database schema definitions, PostgreSQL constraints, and ORM query examples, see [Model Schemas Reference](references/model-schemas.md).
