---
name: warehouse-api-endpoints
description: Use this skill when implementing, inspecting, or debugging RESTful API endpoints, request and response JSON payloads, query parameter filtering, stock adjustment actions, authentication views, or HTTP error responses in the warehouse management system.
---

# Warehouse API Endpoints Skill

This skill defines the complete RESTful API routing contract, HTTP request and response structures, authentication headers, query parameters, and error envelopes for the Warehouse Management Backend.

## API Architecture and View Modules

Views are organized per domain object under `warehouse/views/`:

- `warehouse/views/auth.py`: User registration (`RegisterView`), token login (`LoginView`), and profile retrieval (`UserProfileView`).
- `warehouse/views/warehouse.py`: `WarehouseViewSet` managing warehouse CRUD operations and the nested `/products/` action.
- `warehouse/views/product.py`: `ProductViewSet` managing product CRUD operations, filtering, and the custom `/adjust-stock/` action.
- `warehouse/views/__init__.py`: Re-exports all views and ViewSets for `warehouse/urls.py`.

## Global API Conventions

- **Base URL Prefix**: `/api/v1/`
- **Authentication Header**: Required for all state-changing endpoints (`POST`, `PUT`, `DELETE`):

```http
Authorization: Token <token_key>
```

- **Permission Policy**:
  - `AllowAny`: Read-only queries (`GET /warehouses/`, `GET /products/`), and Auth endpoints (`register/`, `login/`).
  - `IsAuthenticated`: Modifying actions (`POST`, `PUT`, `DELETE`, `/adjust-stock/`) and profile inspection (`GET /auth/me/`).

## Endpoint Catalog (15 Endpoints)

### 1. Authentication Endpoints

- `POST /api/v1/auth/register/`: Create a new user account and obtain initial authentication token.
- `POST /api/v1/auth/login/`: Authenticate username and password credentials; returns Token and user details.
- `GET /api/v1/auth/me/`: Retrieve authenticated user details (requires Token).

### 2. Warehouse Endpoints

- `GET /api/v1/warehouses/`: Retrieve list of all storage facilities.
- `POST /api/v1/warehouses/`: Create a new warehouse facility (requires Token).
- `GET /api/v1/warehouses/{id}/`: Retrieve detailed information for a specific warehouse.
- `PUT /api/v1/warehouses/{id}/`: Update warehouse attributes (requires Token).
- `DELETE /api/v1/warehouses/{id}/`: Remove a warehouse facility (requires Token).
- `GET /api/v1/warehouses/{id}/products/`: Retrieve all products stored within the specified warehouse.

### 3. Product Endpoints

- `GET /api/v1/products/`: Retrieve filtered list of inventory items.
- `POST /api/v1/products/`: Create a new product record assigned to a warehouse (requires Token).
- `GET /api/v1/products/{id}/`: Retrieve specific product details.
- `PUT /api/v1/products/{id}/`: Update product record (requires Token).
- `DELETE /api/v1/products/{id}/`: Delete a product record (requires Token).
- `POST /api/v1/products/{id}/adjust-stock/`: Execute atomic inventory import or export (requires Token).

## Product Query Filters

The `GET /api/v1/products/` endpoint supports four query parameters:

- `warehouse`: Exact match on foreign key ID (e.g. `?warehouse=1`).
- `category`: Case-insensitive match on product category (e.g. `?category=Laptop`).
- `status`: Exact match on inventory status (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`).
- `search`: Case-insensitive substring search matching against `name` and `sku`.

## Stock Adjustment Action Contract

- **Endpoint**: `POST /api/v1/products/{id}/adjust-stock/`
- **Request Body**:

```json
{
  "action": "IMPORT",
  "quantity": 25,
  "note": "Nhập hàng từ nhà cung cấp"
}
```

- **Validation Rules**:
  - `action`: Must be either `"IMPORT"` or `"EXPORT"`.
  - `quantity`: Must be a positive integer greater than or equal to 1.
  - `EXPORT` checks: `quantity` must not exceed current `product.quantity`. Returns HTTP 400 if insufficient.
  - `IMPORT` checks: New total must not exceed `warehouse.capacity`. Returns HTTP 400 if capacity exceeded.

## Detailed Payloads and Error Examples Reference

For complete request and response payloads, status codes, and error formats matching the Postman collection, see [Payloads and Errors Reference](references/payloads-and-errors.md).
