from rest_framework import serializers
from warehouse.models import Product


class ProductSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'warehouse',
            'warehouse_name',
            'sku',
            'name',
            'category',
            'quantity',
            'price',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Số lượng sản phẩm không được là số âm.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Đơn giá sản phẩm không được là số âm.")
        return value
