---
paths:
  - "**/views/**"
  - "**/serializers/**"
  - "**/urls.py"
---

# RESTful API Conventions and Standards

This document specifies API design principles, URL structure, authentication headers, HTTP status code usage, and standardized payload envelopes for the Warehouse Management Backend.

## URL Structure and Routing

- **Base Routing Prefix**: All API endpoints must be served under `/api/v1/`.
- **Resource Collections**: Always use lowercase plural nouns for entity collections:
  - `/api/v1/warehouses/` (Warehouse collection)
  - `/api/v1/products/` (Product collection)
- **Nested Sub-Resources**: Represent parent-child relationships through hierarchical paths:
  - `/api/v1/warehouses/{id}/products/` (All products residing within a specific warehouse)
- **Custom RPC Actions**: Use hyphenated kebab-case for specific remote procedure actions on resources:
  - `POST /api/v1/products/{id}/adjust-stock/` (Stock import and export actions)

## Authentication and Security Headers

- **Header Requirement**: Clients accessing protected endpoints must send an HTTP Authorization header formatted with token authentication:
  - `Authorization: Token <token_key>`
- **Permission Matrix**:
  - Read-only endpoints (`GET`) may allow public access if designated.
  - State-modifying endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) require authenticated user sessions (`IsAuthenticated`).

## Standard HTTP Status Codes

- `200 OK`: Request succeeded for data retrieval (`GET`), standard updates (`PUT`/`PATCH`), or RPC action completion (`POST` adjust-stock).
- `201 Created`: New resource successfully instantiated and persisted (`POST` warehouse or product creation, user registration).
- `204 No Content`: Resource successfully removed with an empty response body (`DELETE`).
- `400 Bad Request`: Input validation failure, malformed JSON body, or business invariant violation (e.g. negative quantity, capacity overflow, insufficient stock for export).
- `401 Unauthorized`: Request lacks valid authentication credentials or includes an invalid token.
- `403 Forbidden`: Authenticated user lacks permission for the requested operation.
- `404 Not Found`: Target resource identifier does not exist in the database.

## Error Response Structure

Error responses must return valid JSON structures providing clear, descriptive messages:

- **Single General Error**:

```json
{
  "error": "Mô tả chi tiết nguyên nhân lỗi"
}
```

- **Field-Level Validation Errors**:

```json
{
  "quantity": [
    "Số lượng điều chỉnh phải lớn hơn 0!"
  ]
}
```

- **Operation Detail Error**:

```json
{
  "detail": "Không tìm thấy thông tin xác thực."
}
```
