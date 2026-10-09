from rest_framework import serializers
from warehouse.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    current_total_quantity = serializers.ReadOnlyField()
    products_count = serializers.ReadOnlyField()

    class Meta:
        model = Warehouse
        fields = [
            'id',
            'name',
            'code',
            'location',
            'capacity',
            'is_active',
            'current_total_quantity',
            'products_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_capacity(self, value):
        # When updating existing warehouse, ensure new capacity is not less than current inventory
        if self.instance:
            current_total = self.instance.current_total_quantity
            if value < current_total:
                raise serializers.ValidationError(
                    "Sức chứa mới không được nhỏ hơn tổng số lượng sản phẩm hiện có trong kho."
                )
        return value
