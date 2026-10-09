---
name: warehouse-management
description: Comprehensive development, domain logic, and testing instructions for the Warehouse Management Backend system built with Django, Django REST Framework, and PostgreSQL.
---

# Warehouse Management System Development Skill

This skill provides complete domain knowledge, architectural guidelines, database schemas, validation rules, and testing workflows for AI agents working on the Warehouse Management backend.

## 1. Domain Models and Database Schema

The system manages physical storage facilities and products stored within them. It runs on PostgreSQL 18 with Django ORM.

### Warehouse Model

- `id`: AutoField (Primary Key)
- `name`: String, maximum 150 characters (Warehouse display name)
- `code`: String, maximum 50 characters, unique (Warehouse unique identifier, e.g. `KHO-HN-01`)
- `location`: String, maximum 255 characters (Physical address)
- `capacity`: Positive integer, minimum 1 (Maximum total units of products this facility can store)
- `is_active`: Boolean (Operational status)
- `current_total_quantity`: Dynamic property computing the sum of all product quantities currently stored in this warehouse
- `created_at`: DateTime, auto-generated on creation
- `updated_at`: DateTime, auto-updated on modification

### Product Model

- `id`: AutoField (Primary Key)
- `warehouse`: ForeignKey referencing `Warehouse`, `related_name='products'`, `on_delete=CASCADE`
- `sku`: String, maximum 60 characters, unique (Stock Keeping Unit identifier, e.g. `SKU-DELL-XPS15`)
- `name`: String, maximum 200 characters (Product title)
- `category`: String, maximum 100 characters (Classification category)
- `quantity`: Positive integer, minimum 0 (Current inventory balance in units)
- `price`: Decimal, max 12 digits, 2 decimal places, minimum 0.00 (Unit selling price)
- `status`: String choice (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`), automatically calculated on save
- `created_at`: DateTime, auto-generated on creation
- `updated_at`: DateTime, auto-updated on modification

## 2. Business Logic and Validation Rules

All operations modifying inventory must strictly enforce the following business constraints:

### Capacity Constraint

- When creating or modifying a product, the total quantity of all items in the designated warehouse must never exceed `Warehouse.capacity`.
- Validation formula: `sum(other_products.quantity) + current_product.quantity <= warehouse.capacity`.
- If the constraint is violated, raise `ValidationError` returning HTTP `400 Bad Request` with an explicit error message.

### Stock Status State Machine

- The `status` field is automatically maintained by the `Product.save()` lifecycle:
  - If `quantity == 0`: `OUT_OF_STOCK`
  - If `0 < quantity <= 10`: `LOW_STOCK`
  - If `quantity > 10`: `IN_STOCK`

### Stock Adjustment Action

- The endpoint `POST /api/v1/products/{id}/adjust-stock/` handles atomic inventory movements:
  - `action="IMPORT"`: Increases `quantity` by specified amount. Must verify total does not exceed warehouse capacity.
  - `action="EXPORT"`: Decreases `quantity` by specified amount. If requested quantity exceeds current stock, abort immediately and return HTTP `400 Bad Request`.
  - `quantity`: Must be an integer greater than or equal to 1. Negative or zero values must be rejected with HTTP `400 Bad Request`.

## 3. Request and Response Payloads

### Stock Adjustment Payload Example

```json
{
  "action": "IMPORT",
  "quantity": 25
}
```

Success Response (`200 OK`):

```json
{
  "message": "Nhập kho thành công 25 sản phẩm",
  "product": {
    "id": 1,
    "sku": "SKU-DELL-XPS15",
    "name": "Dell XPS 15 9530",
    "quantity": 45,
    "status": "IN_STOCK",
    "warehouse": 1
  }
}
```

### Product Creation Payload Example

```json
{
  "sku": "SKU-LOGI-MX3",
  "name": "Chuột Logitech MX Master 3S",
  "category": "Phụ kiện",
  "quantity": 30,
  "price": "2490000.00",
  "warehouse": 1
}
```

## 4. RESTful API Endpoints

The API adheres to REST specifications and returns standardized JSON structures.

### Standard Endpoints

- `GET /api/v1/warehouses/`: Retrieve paginated list of warehouses (HTTP 200 OK)
- `POST /api/v1/warehouses/`: Create new warehouse, requires Token (HTTP 201 Created)
- `GET /api/v1/warehouses/{id}/`: Retrieve warehouse details (HTTP 200 OK / 404 Not Found)
- `GET /api/v1/warehouses/{id}/products/`: Retrieve all products inside specific warehouse (HTTP 200 OK)
- `PUT /api/v1/warehouses/{id}/`: Update warehouse, requires Token (HTTP 200 OK)
- `DELETE /api/v1/warehouses/{id}/`: Delete warehouse, requires Token (HTTP 204 No Content)
- `GET /api/v1/products/`: Retrieve product list with query filters (HTTP 200 OK)
- `POST /api/v1/products/`: Create product, requires Token (HTTP 201 Created / 400 Bad Request)
- `GET /api/v1/products/{id}/`: Retrieve product details (HTTP 200 OK / 404 Not Found)
- `POST /api/v1/products/{id}/adjust-stock/`: Perform import or export (HTTP 200 OK / 400 Bad Request)
- `PUT /api/v1/products/{id}/`: Update product, requires Token (HTTP 200 OK / 400 Bad Request)
- `DELETE /api/v1/products/{id}/`: Delete product, requires Token (HTTP 204 No Content)

### Query Parameters for Product Filtering

- `warehouse`: Filter by integer warehouse ID (e.g. `?warehouse=1`)
- `category`: Case-insensitive category match (e.g. `?category=Phụ kiện`)
- `status`: Exact status filter (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`)
- `search`: Case-insensitive search across `name` and `sku`

## 5. AI Development Workflow

When implementing new features or modifying existing logic, follow this sequence:

1. **Schema Check:** Inspect existing database models in `warehouse/models.py`. Ensure any new models or fields include clear validation methods.
2. **Migrations:** Run `python manage.py makemigrations` and `python manage.py migrate` to apply changes against PostgreSQL.
3. **Serializers:** Define input validation in `warehouse/serializers.py` with field-level validators (`validate_<fieldname>`).
4. **ViewSets:** Keep view methods thin. Delegate business logic to models or custom service functions. Handle exceptions and map them to standard HTTP status codes.
5. **Testing Requirement:** Add comprehensive test cases in `warehouse/tests.py` using `APITestCase`. Every new endpoint must have tests covering success states (200/201), client errors (400), not found states (404), and permission errors (401).

## 6. Verification Checklist

Before completing any task, verify the following:

- [ ] All 12+ unit tests pass: `python manage.py test`
- [ ] System check reports no issues: `python manage.py check`
- [ ] Markdownlint check passes with 0 issues: `npx markdownlint-cli2 ...`
- [ ] No trailing colons or punctuation in Markdown headings
- [ ] Clean separation of concerns between models, serializers, and views
- [ ] No hardcoded database credentials or secret keys in code files
