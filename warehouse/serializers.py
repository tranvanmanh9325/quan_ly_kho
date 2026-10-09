from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Warehouse, Product


class WarehouseSerializer(serializers.ModelSerializer):
    current_total_quantity = serializers.ReadOnlyField()
    products_count = serializers.SerializerMethodField()

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

    def get_products_count(self, obj):
        return obj.products.count()


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


class StockAdjustmentSerializer(serializers.Serializer):
    ACTION_CHOICES = (
        ('IMPORT', 'Nhập kho'),
        ('EXPORT', 'Xuất kho'),
    )

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    quantity = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True, default='')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Tên đăng nhập hoặc mật khẩu không chính xác.")
        if not user.is_active:
            raise serializers.ValidationError("Tài khoản này đã bị vô hiệu hóa.")
        attrs['user'] = user
        return attrs
