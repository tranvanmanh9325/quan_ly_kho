from django.db import models
from django.core.validators import MinValueValidator


class Warehouse(models.Model):
    name = models.CharField(max_length=150, verbose_name="Tên kho")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã kho")
    location = models.CharField(max_length=255, verbose_name="Địa chỉ kho")
    capacity = models.PositiveIntegerField(
        default=1000,
        validators=[MinValueValidator(1)],
        verbose_name="Sức chứa tối đa (sản phẩm)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Kho bãi"
        verbose_name_plural = "Danh sách kho bãi"

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def current_total_quantity(self):
        # Fast-path: return annotated value if set by queryset; Fallback-path: compute aggregate for standalone instance
        if hasattr(self, '_current_total_quantity'):
            return self._current_total_quantity
        total = self.products.aggregate(total=models.Sum('quantity'))['total']
        return total or 0

    @current_total_quantity.setter
    def current_total_quantity(self, value):
        self._current_total_quantity = value

    @property
    def products_count(self):
        # Fast-path: return annotated value if set by queryset; Fallback-path: compute count for standalone instance
        if hasattr(self, '_products_count'):
            return self._products_count
        return self.products.count()

    @products_count.setter
    def products_count(self, value):
        self._products_count = value
