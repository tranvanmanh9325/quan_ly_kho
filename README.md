# Hệ Thống Backend Quản Lý Kho Bãi (Warehouse Management System)

Dự án Backend xây dựng bằng **Python Django 6.x** và **Django REST Framework (DRF)**, kết nối trực tiếp với cơ sở dữ liệu **PostgreSQL 18**.

---

## 1. Yêu cầu & Công nghệ

- **Python**: 3.14+ (Môi trường ảo `venv`)
- **Framework**: Django 6.1.2 & Django REST Framework 3.18.3
- **Database**: PostgreSQL 18.x (`quan_ly_kho_db`)
- **Authentication**: Token Authentication & Basic Auth
- **AI Rules & Skills**: Tích hợp `.claude/rules/CLAUDE.md` và `.claude/skills/warehouse-management/`

---

## 2. Hướng dẫn khởi động nhanh (Quickstart)

### Bước 1: Kích hoạt môi trường ảo & Cài đặt thư viện

```powershell
cd D:\GitHub\codegym\quan_ly_kho
.\venv\Scripts\Activate.ps1

# Cài đặt toàn bộ thư viện nếu thiết lập trên máy mới
pip install -r requirements.txt
```

### Bước 2: Khởi động Server

```powershell
python manage.py runserver 8000
```

Server sẽ chạy tại: `http://127.0.0.1:8000/`

---

## 3. Tài khoản & Dữ liệu mẫu (Đã khởi tạo)

- **Tài khoản quản trị / Nhân viên:**
  - Username: `admin`
  - Password: `AdminPassword123@`
  - Auth Token: `28274206d1225da05d77e02a8d2ee0b1c124086f`
- **Django Admin Web Dashboard:**
  - Truy cập: `http://127.0.0.1:8000/admin/`

---

## 4. Danh sách Endpoint chuẩn RESTful

| Phương thức | Đường dẫn Endpoint | Mô tả | Mã phản hồi |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login/` | Đăng nhập lấy Token | `200 OK` |
| `POST` | `/api/v1/auth/register/` | Đăng ký nhân viên mới | `201 Created` |
| `GET` | `/api/v1/auth/me/` | Xem thông tin user hiện tại | `200 OK` / `401 Unauthorized` |
| `GET` | `/api/v1/warehouses/` | Danh sách kho bãi | `200 OK` |
| `POST` | `/api/v1/warehouses/` | Tạo kho mới (Cần Token) | `201 Created` / `400 Bad Request` |
| `GET` | `/api/v1/warehouses/{id}/` | Chi tiết kho | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/warehouses/{id}/products/` | Lấy danh sách sản phẩm trong kho | `200 OK` |
| `PUT` | `/api/v1/warehouses/{id}/` | Cập nhật kho (Cần Token) | `200 OK` |
| `DELETE` | `/api/v1/warehouses/{id}/` | Xóa kho (Cần Token) | `204 No Content` |
| `GET` | `/api/v1/products/` | Danh sách sản phẩm (có lọc, search) | `200 OK` |
| `POST` | `/api/v1/products/` | Thêm sản phẩm mới (Cần Token) | `201 Created` / `400 Bad Request` |
| `GET` | `/api/v1/products/{id}/` | Chi tiết sản phẩm | `200 OK` / `404 Not Found` |
| `POST` | `/api/v1/products/{id}/adjust-stock/` | Nhập / Xuất kho (Kiểm tra tồn kho) | `200 OK` / `400 Bad Request` |
| `PUT` | `/api/v1/products/{id}/` | Cập nhật sản phẩm (Cần Token) | `200 OK` |
| `DELETE` | `/api/v1/products/{id}/` | Xóa sản phẩm (Cần Token) | `204 No Content` |

---

## 5. Kiểm thử bằng Postman

Import file **`quan_ly_kho_postman_collection.json`** nằm ở thư mục gốc của dự án vào Postman. Bộ sưu tập đã có sẵn biến `base_url` và `token` admin để bạn bấm "Send" kiểm tra ngay lập tức.

---

## 6. Chạy Unit Test

```powershell
python manage.py test
```

Toàn bộ 12 test case bao phủ CRUD, xác thực Token, logic nghiệp vụ xuất nhập kho và bắt lỗi status code (400, 404, 401) đều đã pass 100%.
