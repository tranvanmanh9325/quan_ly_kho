# Hệ Thống Backend Quản Lý Kho Bãi (Warehouse Management System)

Dự án Backend xây dựng bằng **Python 3.14+**, **Django 6.1+** và **Django REST Framework (DRF) 3.18+**, kết nối trực tiếp với cơ sở dữ liệu **PostgreSQL 18**. Hệ thống được thiết kế theo kiến trúc mô-đun hóa theo từng đối tượng (Modular Per-Object Architecture), tích hợp đầy đủ bộ quy chuẩn quản trị AI Governance, chính sách an toàn dữ liệu, xử lý tương tranh an toàn (Concurrency-Safe) và bộ kiểm thử tự động toàn diện (72/72 tests PASS).

---

## 1. Yêu cầu và Công nghệ

- **Ngôn ngữ**: Python 3.14+ (Quản lý qua môi trường ảo `venv`)
- **Web Framework**: Django 6.1.2 & Django REST Framework 3.18.3
- **Cơ sở dữ liệu**: PostgreSQL 18.x (CSDL phát triển: `quan_ly_kho_db`, CSDL kiểm thử: `test_quan_ly_kho_db`)
- **Xác thực và Phân quyền**: Token Authentication (`rest_framework.authtoken`) kết hợp Django Permission Classes
- **Kiểm soát tương tranh**: Khóa bi quan theo thứ tự phân cấp (`select_for_update`) kết hợp giao dịch nguyên tử (`transaction.atomic`) chống tranh chấp dữ liệu (Race Conditions)
- **Hệ thống AI Rules (12 files tập trung trong `.claude/rules/`)**:
  - `CLAUDE.md`: Bộ điều hướng trung tâm (Router & Index) liên kết toàn bộ tài liệu hướng dẫn.
  - `overview-and-stack.md`: Tổng quan kiến trúc hệ thống và ngăn xếp công nghệ.
  - `collaboration-principles.md`: Nguyên tắc cộng tác người - AI, văn hóa Senior Developer và Plan-Before-Code.
  - `python-django-style.md`: Tiêu chuẩn định dạng PEP 8, cú pháp Python/Django (áp dụng theo đường dẫn `**/*.py`).
  - `rest-api-conventions.md`: Quy chuẩn thiết kế RESTful API, cấu trúc URL, chuẩn hóa lỗi `{"error": "..."}`, mã HTTP (áp dụng theo đường dẫn `views`, `serializers`, `urls.py`).
  - `database-and-orm.md`: Nguyên tắc tối ưu hóa truy vấn Django ORM, chống N+1 query (`select_related`, `annotate`), validation nghiệp vụ.
  - `data-safety-and-deletion.md`: Chính sách an toàn dữ liệu, 8 lệnh cấm tuyệt đối với AI, SOP sao lưu và phục hồi.
  - `security-and-secrets.md`: Quy chuẩn bảo mật thông tin nhạy cảm, cơ chế Fail-Fast môi trường, biến môi trường `.env` và xác thực Token.
  - `testing.md`: Tiêu chuẩn kiểm thử tự động, cấu trúc package kiểm thử 72 tests và ma trận kiểm thử tương tranh (áp dụng theo đường dẫn `tests`).
  - `git-and-commits.md`: Quy ước thông điệp Git commit chuẩn Conventional Commits tiếng Anh.
  - `dev-commands.md`: Bảng tra cứu các lệnh CLI chuẩn trong quá trình phát triển dự án.
  - `project-structure.md`: Sơ đồ kiến trúc module hóa per-object và quy ước re-export tương thích ngược.
- **Hệ thống AI Skills (5 skills chuyên biệt theo mô hình Progressive Disclosure trong `.claude/skills/`)**:
  - `warehouse-domain-model`: Mô hình nghiệp vụ kho hàng, bất biến sức chứa (Capacity Invariant) và máy trạng thái tồn kho (Stock Status State Machine).
  - `warehouse-api-endpoints`: Đặc tả chi tiết các API endpoints, cấu trúc payload JSON, bộ lọc truy vấn và định dạng phản hồi chuẩn REST `{"error": "..."}`.
  - `warehouse-testing`: Cẩm nang kiểm thử với `BaseWarehouseTestCase`, công thức viết test case, kiểm thử đa luồng với `TransactionTestCase` và ma trận 72 test cases.
  - `warehouse-db-migrations-and-safety`: Quy trình quản lý migration an toàn, SOP sao lưu `pg_dump` và sổ tay xử lý sự cố.
  - `warehouse-feature-workflow`: Quy trình phát triển tính năng 4 giai đoạn, checklist rà soát mã nguồn và kiểm chứng thực tế.

---

## 2. Cấu trúc Thư mục Dự án

Mã nguồn được tổ chức theo cấu trúc mô-đun hóa theo từng đối tượng (Per-Object Modularization), loại bỏ triệt để các file nguyên khối cồng kềnh và tách biệt tầng xử lý nghiệp vụ thông qua Service Layer:

```text
quan_ly_kho/
├── .claude/
│   ├── rules/                          # 12 quy tắc quản trị AI tập trung
│   │   ├── CLAUDE.md                   # Router và Index chính
│   │   ├── overview-and-stack.md
│   │   ├── collaboration-principles.md
│   │   ├── python-django-style.md
│   │   ├── rest-api-conventions.md
│   │   ├── database-and-orm.md
│   │   ├── data-safety-and-deletion.md
│   │   ├── security-and-secrets.md
│   │   ├── testing.md
│   │   ├── git-and-commits.md
│   │   ├── dev-commands.md
│   │   └── project-structure.md
│   └── skills/                         # 5 AI skills kèm tài liệu tham khảo sâu
│       ├── warehouse-domain-model/
│       ├── warehouse-api-endpoints/
│       ├── warehouse-testing/
│       ├── warehouse-db-migrations-and-safety/
│       └── warehouse-feature-workflow/
├── warehouse/                          # Ứng dụng chính Quản lý kho bãi
│   ├── models/                         # Mô-đun dữ liệu theo từng thực thể
│   │   ├── __init__.py                 # Re-export Warehouse, Product, StockStatus
│   │   ├── warehouse.py                # Model Warehouse và property tính tổng tồn kho
│   │   └── product.py                  # Model Product, StockStatus và validation
│   ├── serializers/                    # Mô-đun tuần tự hóa và kiểm định dữ liệu
│   │   ├── __init__.py                 # Re-export toàn bộ 5 serializers
│   │   ├── warehouse.py                # WarehouseSerializer
│   │   ├── product.py                  # ProductSerializer
│   │   ├── stock_adjustment.py         # StockAdjustmentSerializer
│   │   └── auth.py                     # UserRegisterSerializer, UserLoginSerializer
│   ├── views/                          # Mô-đun điều khiển API endpoints
│   │   ├── __init__.py                 # Re-export toàn bộ ViewSets và APIViews
│   │   ├── warehouse.py                # WarehouseViewSet và action /products/
│   │   ├── product.py                  # ProductViewSet, bộ lọc và action /adjust-stock/
│   │   └── auth.py                     # RegisterView, LoginView, UserProfileView
│   ├── services/                       # Tầng xử lý nghiệp vụ độc lập (Lean Service Layer)
│   │   ├── __init__.py                 # Re-export dịch vụ xuất nhập kho và exceptions
│   │   └── stock_service.py            # Hàm adjust_product_stock() với select_for_update
│   ├── tests/                          # Package kiểm thử tự động toàn diện (72 tests)
│   │   ├── __init__.py                 # Expose các lớp kiểm thử cho discovery
│   │   ├── base.py                     # BaseWarehouseTestCase cung cấp dữ liệu mẫu
│   │   ├── test_warehouse_api.py       # Kiểm thử API Kho bãi & Query Count (19 test cases)
│   │   ├── test_product_api.py         # Kiểm thử API Sản phẩm và bộ lọc (23 test cases)
│   │   ├── test_stock_adjustment.py    # Kiểm thử nghiệp vụ Xuất/Nhập kho (16 test cases)
│   │   ├── test_auth.py                # Kiểm thử Đăng ký/Đăng nhập/Profile (10 test cases)
│   │   └── test_concurrency.py         # Kiểm thử tương tranh đa luồng trên PG (4 test cases)
│   ├── migrations/
│   │   └── 0001_initial.py             # Migration khởi tạo cơ sở dữ liệu ban đầu
│   ├── management/commands/
│   │   └── seed_data.py                # Lệnh nạp dữ liệu mẫu an toàn (không log bí mật)
│   ├── admin.py                        # Giao diện quản trị Django Admin
│   ├── apps.py                         # Cấu hình ứng dụng Warehouse
│   └── urls.py                         # Routing các API endpoints của ứng dụng
├── config/                             # Cấu hình dự án Django
│   ├── settings.py                     # Cấu hình môi trường Fail-Fast, CSDL, CORS, REST
│   ├── urls.py                         # Routing cấp dự án và API root
│   ├── wsgi.py
│   └── asgi.py
├── manage.py                           # Điểm nhập lệnh điều hành Django CLI
├── quan_ly_kho_postman_collection.json # Bộ sưu tập kiểm thử Postman tích hợp biến an toàn
├── requirements.txt                    # Danh sách các gói thư viện phụ thuộc
├── .env.example                        # Mẫu biến môi trường an toàn (không lộ bí mật)
└── README.md                           # Tài liệu hướng dẫn dự án
```

---

## 3. Chính sách An toàn Dữ liệu và Cơ sở Dữ liệu

Nhằm bảo vệ dữ liệu kinh doanh quan trọng và ngăn ngừa sự cố ngoài ý muốn, dự án áp dụng nghiêm ngặt chính sách an toàn dữ liệu:

### Nguyên tắc Xóa Dữ liệu Nghiệp vụ (Soft Delete vs Hard Delete)

- **Thực thể kinh doanh cốt lõi**: `Warehouse` (Kho bãi) và `Product` (Hàng hóa) đại diện cho tài sản và số liệu kế toán thực tế. Dữ liệu này phải tuân thủ mẫu thiết kế **Soft Delete** (`is_deleted = True`, `deleted_at = timezone.now()`), không xóa vật lý khỏi bảng PostgreSQL để lưu vết lịch sử kiểm toán.
- **Xóa vật lý (Hard Delete)**: Chỉ được phép áp dụng cho các dữ liệu mang tính tạm thời, ngắn hạn như Authentication Token đã hết hạn (`authtoken_token`) hoặc phiên làm việc tạm (sessions).
- **Rủi ro xóa tầng (Cascade Deletion)**: Mối quan hệ giữa `Product` và `Warehouse` hiện đang cấu hình `on_delete=models.CASCADE`. Khi một kho bãi bị xóa, toàn bộ hàng hóa trong kho sẽ bị xóa dây chuyền. Đội ngũ kỹ sư khuyến nghị nâng cấp sang `models.PROTECT` ở phiên bản tiếp theo để ngăn ngừa việc vô tình xóa mất sổ sách kho đang có hàng tồn.

### 8 Lệnh Cấm Tuyệt Đối Đối Với AI Agents

Các AI Agents tuyệt đối **KHÔNG ĐƯỢC PHÉP** tự ý thực thi các thao tác sau nếu không có văn bản phê duyệt trực tiếp từ kỹ sư quản lý:

1. **Phá hủy CSDL hoặc Bảng**: Thực thi `dropdb`, `DROP DATABASE`, `DROP SCHEMA`, hoặc `DROP TABLE`.
2. **Xóa sạch dữ liệu qua Flush**: Chạy lệnh `python manage.py flush`.
3. **Đảo ngược Migration**: Chạy lệnh `python manage.py migrate <app> zero` hoặc lùi migration về trạng thái cũ.
4. **Xóa hoặc sửa file Migration**: Xóa hoặc đổi tên các tệp migration đã có (ví dụ `0001_initial.py`).
5. **Reset CSDL phát triển**: Xóa, tạo lại hoặc làm rỗng cơ sở dữ liệu `quan_ly_kho_db`.
6. **Lệnh dọn bảng mức thấp**: Thực thi câu lệnh SQL `TRUNCATE` hoặc `TRUNCATE TABLE ... CASCADE`.
7. **Xóa hàng loạt không kiểm soát**: Thực thi `Model.objects.all().delete()` hoặc xóa QuerySet diện rộng mà không có điều kiện `filter()` cụ thể.
8. **Chỉnh sửa Migration đã áp dụng**: Thay đổi nội dung các tệp mã nguồn migration đã được thực thi trên bất kỳ database nào.

### Quy Trình Vận Hành An Toàn 5 Bước (SOP)

Khi phát sinh nhu cầu bảo trì dữ liệu hoặc thay đổi cấu trúc bảng:

1. **Sao lưu trước tiên (Backup First)**: Tạo bản sao lưu nhị phân đầy đủ bằng lệnh `pg_dump`:

   ```powershell
   pg_dump -U postgres -h localhost -p 5432 -d quan_ly_kho_db -F c -b -v -f backup_quan_ly_kho.dump
   ```

2. **Thử nghiệm trên Sandbox**: Kiểm tra script hoặc migration trên cơ sở dữ liệu thử nghiệm độc lập trước khi áp dụng vào môi trường phát triển.
3. **Xác thực ngữ cảnh môi trường**: Kiểm tra kỹ biến môi trường (`DB_NAME`, `DB_HOST`), tuyệt đối không thao tác nhầm trên staging/production.
4. **Yêu cầu phê duyệt từ con người (Human-in-the-loop)**: Trình bày kế hoạch chi tiết, số lượng bản ghi chịu ảnh hưởng và chờ sự phê duyệt rõ ràng từ người dùng.
5. **Kế hoạch phục hồi (Rollback Plan)**: Sẵn sàng câu lệnh phục hồi khẩn cấp bằng `pg_restore`:

   ```powershell
   pg_restore -U postgres -h localhost -p 5432 -d quan_ly_kho_db -c -v backup_quan_ly_kho.dump
   ```

### Cô Lập Hoàn Toàn Cơ Sở Dữ Liệu Kiểm Thử

Khi thực thi lệnh `python manage.py test`, Django sẽ tự động khởi tạo cơ sở dữ liệu kiểm thử độc lập mang tên `test_quan_ly_kho_db`. Mọi hành động ghi, sửa, xóa trong suốt quá trình chạy test case diễn ra 100% trong môi trường cô lập này và tự động bị hủy sau khi hoàn thành, đảm bảo dữ liệu phát triển thực tế tại `quan_ly_kho_db` không bao giờ bị ảnh hưởng.

---

## 4. Hướng dẫn Khởi động Nhanh (Quickstart)

### Bước 1 - Kích hoạt môi trường ảo và cài đặt thư viện

```powershell
cd D:\GitHub\codegym\quan_ly_kho
.\venv\Scripts\Activate.ps1

# Cài đặt các gói phụ thuộc cần thiết
pip install -r requirements.txt
```

### Bước 2 - Thiết lập Biến Môi trường An toàn (Fail-Fast Configuration)

Sao chép tệp mẫu `.env.example` thành `.env` tại thư mục gốc của dự án:

```powershell
Copy-Item .env.example .env
```

Hệ thống áp dụng cơ chế **Fail-Fast**: nếu thiếu bất kỳ biến môi trường thiết yếu nào (`SECRET_KEY`, `DB_PASSWORD`), ứng dụng sẽ ném ngay lập tức ngoại lệ `RuntimeError` và dừng khởi động để bảo vệ hệ thống, tuyệt đối không sử dụng giá trị ngầm định thiếu an toàn:

```env
# config/.env
DEBUG=True
SECRET_KEY=khoi-tao-khoa-bao-mat-django-ngau-nhien-it-nhat-50-ky-tu-tai-day
DB_NAME=quan_ly_kho_db
DB_USER=postgres
DB_PASSWORD=mat_khau_csdl_cua_ban
DB_HOST=127.0.0.1
DB_PORT=5432

# Danh sách host và CORS được phép truy cập (cách nhau bởi dấu phẩy)
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Mật khẩu khởi tạo cho tài khoản admin trong lệnh seed_data (tùy chọn)
SEED_ADMIN_PASSWORD=MatKhauAdminQuanLyKho2026@
```

### Bước 3 - Kiểm tra hệ thống và tính toàn vẹn của CSDL

```powershell
# Kiểm tra cấu hình và mã nguồn Django (phải báo 0 issues)
python manage.py check

# Đảm bảo không phát sinh migration ngoài ý muốn
python manage.py makemigrations --check --dry-run
```

### Bước 4 - Khởi động Server phát triển

```powershell
python manage.py runserver 8000
```

Dịch vụ sẵn sàng phục vụ tại: `http://127.0.0.1:8000/`

---

## 5. Quản trị Tài khoản và Dữ liệu Mẫu An toàn

### Tài khoản Quản trị viên và Lệnh `seed_data` An toàn

- **Tài khoản mặc định**: `admin`
- **Cơ chế thiết lập mật khẩu an toàn**:
  - Khi chạy `python manage.py seed_data`, hệ thống ưu tiên đọc mật khẩu từ biến môi trường `SEED_ADMIN_PASSWORD`.
  - Nếu biến này không được khai báo, hệ thống sẽ tự động sinh một mật khẩu ngẫu nhiên bảo mật cao (16 ký tự an toàn) và chỉ hiển thị trên màn hình console đúng một lần để quản trị viên lưu lại.
  - Tuyệt đối **không hardcode** mật khẩu trong mã nguồn và **không ghi log token** xác thực ra console hoặc tệp tin để đảm bảo an toàn bí mật 100%.
- **Lấy Auth Token**: Sử dụng API `POST /api/v1/auth/login/` với thông tin tài khoản để nhận Token động.
- **Giao diện quản trị Django Admin**: Truy cập tại `http://127.0.0.1:8000/admin/`.

---

## 6. Danh sách API Endpoints Chuẩn RESTful

Hệ thống cung cấp đầy đủ các endpoints phục vụ quản lý kho, hàng hóa, giao dịch xuất nhập và xác thực tài khoản:

| Phương thức | Đường dẫn Endpoint | Mô tả chức năng | Yêu cầu Auth | Mã HTTP phản hồi |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API Root hiển thị danh mục endpoint | Công khai | `200 OK` |
| `POST` | `/api/v1/auth/login/` | Đăng nhập hệ thống, nhận Auth Token | Công khai | `200 OK` / `400 Bad Request` |
| `POST` | `/api/v1/auth/register/` | Đăng ký tài khoản nhân viên mới | Công khai | `201 Created` / `400 Bad Request` |
| `GET` | `/api/v1/auth/me/` | Xem thông tin hồ sơ tài khoản hiện tại | Token Auth | `200 OK` / `401 Unauthorized` |
| `GET` | `/api/v1/warehouses/` | Lấy danh sách toàn bộ kho bãi (tối ưu O(1) query) | Công khai | `200 OK` |
| `POST` | `/api/v1/warehouses/` | Tạo kho bãi mới | Token Auth | `201 Created` / `400 Bad Request` |
| `GET` | `/api/v1/warehouses/{id}/` | Xem thông tin chi tiết một kho bãi | Công khai | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/warehouses/{id}/products/` | Lấy danh sách hàng hóa thuộc kho (phân trang) | Công khai | `200 OK` / `404 Not Found` |
| `PUT` | `/api/v1/warehouses/{id}/` | Cập nhật toàn diện thông tin kho bãi | Token Auth | `200 OK` / `400 Bad Request` / `404 Not Found` |
| `DELETE` | `/api/v1/warehouses/{id}/` | Xóa kho bãi khỏi hệ thống | Token Auth | `204 No Content` / `404 Not Found` |
| `GET` | `/api/v1/products/` | Danh sách hàng hóa (hỗ trợ lọc và tìm kiếm) | Công khai | `200 OK` |
| `POST` | `/api/v1/products/` | Tạo sản phẩm mới trong kho | Token Auth | `201 Created` / `400 Bad Request` |
| `GET` | `/api/v1/products/{id}/` | Xem chi tiết thông tin sản phẩm | Công khai | `200 OK` / `404 Not Found` |
| `PUT` | `/api/v1/products/{id}/` | Cập nhật thông tin hàng hóa | Token Auth | `200 OK` / `400 Bad Request` / `404 Not Found` |
| `DELETE` | `/api/v1/products/{id}/` | Xóa sản phẩm khỏi kho | Token Auth | `204 No Content` / `404 Not Found` |
| `POST` | `/api/v1/products/{id}/adjust-stock/` | Điều chỉnh Nhập / Xuất kho an toàn tương tranh | Token Auth | `200 OK` / `400 Bad Request` / `404 Not Found` |

### Quy Chuẩn Định Dạng Phản Hồi Lỗi Chuẩn RESTful

Hệ thống đã chuẩn hóa toàn diện cấu trúc phản hồi lỗi, tuân thủ nguyên tắc `rest-api-conventions.md`:

#### 1. Lỗi Nghiệp Vụ Toàn Cục (Domain / Business Logic Errors)

Áp dụng cho các vi phạm bất biến nghiệp vụ (như xuất kho vượt tồn kho, nhập kho vượt sức chứa kho):

```json
{
  "error": "Số lượng tồn kho không đủ để xuất! Hiện tại chỉ còn 5, yêu cầu xuất 20."
}
```

#### 2. Lỗi Kiểm Định Theo Trường (Field-Level Validation Errors)

Áp dụng cho các kiểm tra tính hợp lệ dữ liệu đầu vào của Serializer:

```json
{
  "quantity": [
    "Số lượng điều chỉnh phải lớn hơn 0!"
  ]
}
```

#### 3. Bảng So Sánh Cải Tiến Định Dạng Lỗi (Before vs After)

| Kịch bản Lỗi | Định dạng Cũ (Legacy) | Định dạng Mới Chuẩn REST (Current) | Mã HTTP |
| :--- | :--- | :--- | :--- |
| Xuất vượt tồn kho | `{"error": "BAD_REQUEST", "message": "..."}` | `{"error": "Số lượng tồn kho không đủ để xuất!..."}` | `400 Bad Request` |
| Nhập vượt sức chứa | `{"error": "BAD_REQUEST", "message": "..."}` | `{"error": "Tổng số lượng sản phẩm... vượt quá sức chứa..."}` | `400 Bad Request` |
| Số lượng âm/bằng 0 | `{"quantity": ["..."]}` | `{"quantity": ["Số lượng điều chỉnh phải lớn hơn 0!"]}` | `400 Bad Request` |
| Không có Token | `{"detail": "..."}` | `{"detail": "Authentication credentials were not provided."}` | `401 Unauthorized` |
| Không tìm thấy | `{"detail": "Not found."}` | `{"detail": "No Product matches the given query."}` | `404 Not Found` |

### Các Tham Số Truy Vấn Hỗ Trợ Cho Danh Sách Sản Phẩm

Tại endpoint `GET /api/v1/products/`, hệ thống hỗ trợ kết hợp các tham số URL query:

- `?warehouse=<id>`: Lọc sản phẩm theo ID của kho bãi (ví dụ `?warehouse=1`).
- `?category=<tên_danh_mục>`: Lọc sản phẩm theo phân loại danh mục không phân biệt chữ hoa/thường (ví dụ `?category=Laptop`).
- `?status=<IN_STOCK|LOW_STOCK|OUT_OF_STOCK>`: Lọc theo trạng thái tồn kho (Còn hàng, Sắp hết hàng, Hết hàng).
- `?search=<từ_khóa>`: Tìm kiếm tương đối theo tên sản phẩm hoặc mã SKU (ví dụ `?search=Dell`).

### Quy Chuẩn Body Cho Thao Tác Nhập / Xuất Kho

Khi gọi `POST /api/v1/products/{id}/adjust-stock/`:

```json
{
  "action": "IMPORT",
  "quantity": 20,
  "note": "Nhập hàng bổ sung đợt 1"
}
```

- `action`: Bắt buộc là `IMPORT` (nhập thêm) hoặc `EXPORT` (xuất bớt).
- `quantity`: Số lượng nguyên dương lớn hơn 0.
- `note`: Ghi chú tùy chọn cho thao tác điều chỉnh kho.

---

## 7. Hướng dẫn Kiểm thử Tự động (Automated Test Suite)

Dự án sở hữu bộ kiểm thử tự động toàn diện với **72 test cases**, tổ chức dạng package mô-đun hóa trong `warehouse/tests/`, bảo đảm 100% tỷ lệ pass:

### Cấu trúc Gói Kiểm thử (72 Test Cases)

- `warehouse/tests/base.py`: Chứa lớp cơ sở `BaseWarehouseTestCase` kế thừa từ `rest_framework.test.APITestCase`. Tự động tạo người dùng kiểm thử (`teststaff`), sinh token xác thực và tạo sẵn dữ liệu mẫu về kho bãi và sản phẩm, giúp mã kiểm thử tuân thủ nguyên lý DRY.
- `warehouse/tests/test_warehouse_api.py` (**19 test cases**):
  - Lấy danh sách kho bãi, xem chi tiết kho, tạo mới kho thành công.
  - Bắt lỗi khi trùng mã kho (`code`), cập nhật kho thành công, xóa kho thành công.
  - Lấy danh sách sản phẩm theo kho qua endpoint phụ `/products/` kèm phân trang.
  - Bắt lỗi `401 Unauthorized` khi tạo, sửa, xóa kho không có Token.
  - Bắt lỗi `404 Not Found` khi cập nhật kho không tồn tại.
  - Kiểm tra bắt lỗi giảm sức chứa kho xuống thấp hơn lượng hàng tồn hiện tại (`400 Bad Request`).
  - **Chứng minh số lượng truy vấn không đổi (Constant SQL Query Count)**: Sử dụng `assertNumQueries` chứng minh endpoint danh sách kho chạy đúng số lượng câu truy vấn không đổi nhờ `annotate(Sum/Count)`.
- `warehouse/tests/test_product_api.py` (**23 test cases**):
  - Lấy danh sách sản phẩm, xem chi tiết sản phẩm, tạo mới sản phẩm thành công.
  - Bắt lỗi số lượng âm (`quantity < 0`), đơn giá âm (`price < 0`), mã SKU trùng lặp.
  - Bắt lỗi khi tạo hoặc cập nhật sản phẩm vượt quá sức chứa tối đa của kho.
  - Cập nhật sản phẩm thành công (PUT và PATCH).
  - Bắt lỗi `401 Unauthorized` khi thao tác ghi không có Token xác thực.
  - Bắt lỗi `404 Not Found` khi truy vấn sản phẩm không tồn tại.
  - Lọc sản phẩm theo kho bãi (`?warehouse=`), danh mục (`?category=`), trạng thái tồn kho (`?status=`).
  - Tìm kiếm sản phẩm theo tên và mã SKU (`?search=`).
- `warehouse/tests/test_stock_adjustment.py` (**16 test cases**):
  - Nhập kho thành công và cập nhật lại trạng thái tồn kho.
  - Xuất kho thành công và tự động chuyển trạng thái sang `LOW_STOCK` (khi tồn kho <= 10).
  - Bắt lỗi khi xuất kho vượt quá số lượng tồn kho khả dụng (`400 Bad Request`).
  - Bắt lỗi khi hành động điều chỉnh không hợp lệ (ngoài `IMPORT` và `EXPORT`).
  - Bắt lỗi khi số lượng điều chỉnh nhỏ hơn hoặc bằng 0 (`400 Bad Request`).
  - Bắt lỗi khi nhập kho làm tổng số lượng vượt quá sức chứa tối đa của kho.
  - Bắt lỗi `401 Unauthorized` khi điều chỉnh tồn kho không có Token.
  - Bắt lỗi `404 Not Found` khi điều chỉnh tồn kho sản phẩm không tồn tại.
  - Kiểm tra đầy đủ chu trình chuyển đổi trạng thái tồn kho (`IN_STOCK` <-> `LOW_STOCK` <-> `OUT_OF_STOCK`).
  - Xác minh cấu trúc phản hồi lỗi chuẩn REST `{"error": "..."}`.
- `warehouse/tests/test_auth.py` (**10 test cases**):
  - Đăng nhập thành công trả về Auth Token và thông tin người dùng.
  - Đăng nhập thất bại khi sai thông tin tài khoản (`400 Bad Request`).
  - Đăng nhập thất bại khi tài khoản bị vô hiệu hóa (`is_active=False`).
  - Đăng ký nhân viên mới thành công trả về mã `201 Created` và Token.
  - Đăng ký thất bại khi trùng tên người dùng (`username`) hoặc mật khẩu quá ngắn.
  - Đăng ký và đăng nhập thất bại khi thiếu các trường bắt buộc.
  - Xem hồ sơ cá nhân (`/auth/me/`) thành công khi có Token.
  - Bắt lỗi `401 Unauthorized` khi xem hồ sơ cá nhân mà không truyền Token.
- `warehouse/tests/test_concurrency.py` (**4 test cases chuyên sâu**):
  - **Kiểm thử xuất hàng đồng thời (Concurrent Export)**: Khởi chạy 50 luồng xuất hàng song song trên PostgreSQL thực tế. Sử dụng cơ chế khóa bi quan `select_for_update` chứng minh số lượng tồn kho không bao giờ bị âm và không bị thất thoát cập nhật (Lost Updates).
  - **Kiểm thử nhập hàng đồng thời (Concurrent Import)**: Khởi chạy nhiều luồng nhập hàng đồng thời, khóa cấp độ Warehouse bảo đảm tổng số lượng hàng không bao giờ vượt quá sức chứa tối đa (`capacity`).
  - **Kiểm thử gọi API đồng thời**: Khởi chạy đa luồng gọi HTTP API `/adjust-stock/` song song, bảo đảm tính toàn vẹn trạng thái.
  - **Kiểm thử chống Deadlock**: Chạy lặp lại các chuỗi giao dịch đồng thời đảm bảo không phát sinh deadlock trong cơ sở dữ liệu.

### Lệnh Chạy Toàn Bộ Bộ Kiểm Thử

```powershell
# Chạy toàn bộ 72 test cases của dự án
python manage.py test
```

### Lệnh Chạy Riêng Từng Phân Hệ Kiểm Thử

```powershell
# Chạy kiểm thử API Kho bãi và Query Count
python manage.py test warehouse.tests.test_warehouse_api

# Chạy kiểm thử API Sản phẩm và Bộ lọc
python manage.py test warehouse.tests.test_product_api

# Chạy kiểm thử Nghiệp vụ Xuất/Nhập kho
python manage.py test warehouse.tests.test_stock_adjustment

# Chạy kiểm thử Xác thực & Phân quyền
python manage.py test warehouse.tests.test_auth

# Chạy kiểm thử Tương tranh đa luồng trên PostgreSQL
python manage.py test warehouse.tests.test_concurrency
```

Kết quả thực tế: Toàn bộ **72/72 test cases PASS 100%**, thực thi hoàn toàn trong CSDL kiểm thử cô lập `test_quan_ly_kho_db`.

---

## 8. Kiểm thử Bằng Postman

Dự án cung cấp sẵn tệp cấu hình Postman hoàn chỉnh: **`quan_ly_kho_postman_collection.json`** tại thư mục gốc.

Các bước sử dụng:

1. Mở ứng dụng Postman, chọn **Import** và kéo thả tệp `quan_ly_kho_postman_collection.json`.
2. Bộ sưu tập đã tích hợp sẵn các biến (Collection Variables):
   - `base_url`: `http://127.0.0.1:8000`
   - `admin_password`: `<your_admin_password>` (Điền mật khẩu quản trị viên tương ứng của bạn)
   - `token`: `<your_token>` (Tự động lưu và cập nhật sau khi gọi request Đăng nhập thành công)
3. Bộ sưu tập bao gồm 4 thư mục kiểm thử có sẵn dữ liệu mẫu:
   - **1. Authentication**: Đăng nhập (tự lưu token), đăng ký nhân viên mới, xem hồ sơ cá nhân.
   - **2. Warehouses**: Danh sách kho, chi tiết kho, sản phẩm trong kho, tạo kho mới, cập nhật kho, xóa kho.
   - **3. Products**: Danh sách sản phẩm, lọc theo trạng thái tồn kho, tìm kiếm, xem chi tiết, cập nhật, tạo mới, nhập hàng, xuất hàng, xóa sản phẩm.
   - **4. Error Cases**: Kiểm tra phản hồi mã lỗi `400 Bad Request` (số lượng âm, xuất vượt tồn, nhập vượt sức chứa), `401 Unauthorized` (thiếu token), `404 Not Found` (kho/sản phẩm không tồn tại).
