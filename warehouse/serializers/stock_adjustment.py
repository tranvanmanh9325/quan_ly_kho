from rest_framework import serializers


class StockAdjustmentSerializer(serializers.Serializer):
    ACTION_CHOICES = (
        ('IMPORT', 'Nhập kho'),
        ('EXPORT', 'Xuất kho'),
    )

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    quantity = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True, default='')
