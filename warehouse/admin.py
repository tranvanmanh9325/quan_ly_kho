from django.contrib import admin
from .models import Warehouse, Product


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'location', 'capacity', 'current_total_quantity', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'location')
    list_filter = ('is_active',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'warehouse', 'category', 'quantity', 'price', 'status', 'created_at')
    search_fields = ('sku', 'name', 'category')
    list_filter = ('warehouse', 'status', 'category')
