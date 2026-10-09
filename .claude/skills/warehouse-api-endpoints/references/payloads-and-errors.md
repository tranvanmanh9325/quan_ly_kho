# API Payloads and Errors Reference

This document provides request and response JSON payloads, HTTP headers, status codes, and error formats for all 15 API endpoints and test scenarios.

## Authentication Payloads

### POST `/api/v1/auth/login/`

- **Request**:

```json
{
  "username": "admin",
  "password": "<your_admin_password>"
}
```

- **Success Response (HTTP 200 OK)**:

```json
{
  "token": "<your_token>",
  "user_id": 1,
  "username": "admin",
  "email": "admin@example.com"
}
```

### POST `/api/v1/auth/register/`

- **Request**:

```json
{
  "username": "nvkho01",
  "password": "securepassword123",
  "email": "nvkho01@example.com",
  "first_name": "Nguyen",
  "last_name": "Van A"
}
```

- **Success Response (HTTP 201 Created)**:

```json
{
  "token": "<your_token>",
  "user_id": 2,
  "username": "nvkho01",
  "email": "nvkho01@example.com"
}
```

### GET `/api/v1/auth/me/`

- **Headers**: `Authorization: Token <your_token>`
- **Success Response (HTTP 200 OK)**:

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User"
}
```

## Warehouse Payloads

### POST `/api/v1/warehouses/`

- **Headers**: `Authorization: Token <token_key>`
- **Request**:

```json
{
  "name": "Kho Đà Nẵng Trung Tâm",
  "code": "KHO-DN-01",
  "location": "Quận Hải Châu, Đà Nẵng",
  "capacity": 300,
  "is_active": true
}
```

- **Success Response (HTTP 201 Created)**:

```json
{
  "id": 3,
  "name": "Kho Đà Nẵng Trung Tâm",
  "code": "KHO-DN-01",
  "location": "Quận Hải Châu, Đà Nẵng",
  "capacity": 300,
  "is_active": true,
  "current_total_quantity": 0,
  "created_at": "2026-10-09T08:00:00Z",
  "updated_at": "2026-10-09T08:00:00Z"
}
```

### GET `/api/v1/warehouses/{id}/`

- **Success Response (HTTP 200 OK)**:

```json
{
  "id": 1,
  "name": "Kho Hà Nội 01",
  "code": "KHO-HN-01",
  "location": "Khu công nghiệp Bắc Thăng Long, Hà Nội",
  "capacity": 500,
  "is_active": true,
  "current_total_quantity": 125,
  "created_at": "2026-10-01T00:00:00Z",
  "updated_at": "2026-10-01T00:00:00Z"
}
```

## Product Payloads

### POST `/api/v1/products/`

- **Headers**: `Authorization: Token <token_key>`
- **Request**:

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

- **Success Response (HTTP 201 Created)**:

```json
{
  "id": 5,
  "sku": "SKU-LOGI-MX3",
  "name": "Chuột Logitech MX Master 3S",
  "category": "Phụ kiện",
  "quantity": 30,
  "price": "2490000.00",
  "status": "IN_STOCK",
  "warehouse": 1,
  "created_at": "2026-10-09T08:30:00Z",
  "updated_at": "2026-10-09T08:30:00Z"
}
```

### POST `/api/v1/products/{id}/adjust-stock/` (IMPORT)

- **Headers**: `Authorization: Token <token_key>`
- **Request**:

```json
{
  "action": "IMPORT",
  "quantity": 25,
  "note": "Nhập thêm 25 máy"
}
```

- **Success Response (HTTP 200 OK)**:

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

### POST `/api/v1/products/{id}/adjust-stock/` (EXPORT)

- **Headers**: `Authorization: Token <token_key>`
- **Request**:

```json
{
  "action": "EXPORT",
  "quantity": 40,
  "note": "Xuất giao cho đối tác"
}
```

- **Success Response (HTTP 200 OK)**:

```json
{
  "message": "Xuất kho thành công 40 sản phẩm",
  "product": {
    "id": 1,
    "sku": "SKU-DELL-XPS15",
    "name": "Dell XPS 15 9530",
    "quantity": 5,
    "status": "LOW_STOCK",
    "warehouse": 1
  }
}
```

## Standard Error Response Examples

### HTTP 400 Bad Request — Negative Quantity

- **Response Payload**:

```json
{
  "quantity": [
    "Số lượng điều chỉnh phải lớn hơn 0!"
  ]
}
```

### HTTP 400 Bad Request — Export Exceeds Available Stock

- **Response Payload**:

```json
{
  "error": "Số lượng tồn kho không đủ để xuất! Hiện tại chỉ còn 5, yêu cầu xuất 20."
}
```

### HTTP 400 Bad Request — Import Exceeds Warehouse Capacity

- **Response Payload**:

```json
{
  "error": "Tổng số lượng sản phẩm (510) vượt quá sức chứa tối đa của kho (500)!"
}
```

### HTTP 401 Unauthorized — Missing Authentication Token

- **Response Payload**:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### HTTP 404 Not Found — Resource ID Does Not Exist

- **Response Payload**:

```json
{
  "detail": "No Warehouse matches the given query."
}
```
