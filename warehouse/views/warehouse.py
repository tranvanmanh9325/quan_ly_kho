from django.db import transaction
from django.db.models import Sum, Count, Value, IntegerField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from warehouse.models import Warehouse
from warehouse.serializers import WarehouseSerializer, ProductSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Warehouses.
    GET /api/v1/warehouses/ -> 200 OK (List)
    POST /api/v1/warehouses/ -> 201 Created
    GET /api/v1/warehouses/{id}/ -> 200 OK / 404 Not Found
    PUT /api/v1/warehouses/{id}/ -> 200 OK / 400 Bad Request / 404 Not Found
    DELETE /api/v1/warehouses/{id}/ -> 204 No Content / 404 Not Found
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    def get_permissions(self):
        # Allow read actions for all, require authentication for write actions
        if self.action in ['list', 'retrieve', 'products']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Annotate totals at DB level to prevent N+1 queries when serializing lists
        return Warehouse.objects.annotate(
            current_total_quantity=Coalesce(
                Sum('products__quantity'),
                Value(0),
                output_field=IntegerField()
            ),
            products_count=Count('products', distinct=True)
        ).order_by('-created_at')

    @transaction.atomic
    def perform_update(self, serializer):
        # Lock warehouse row to serialize concurrent capacity changes and stock movements
        warehouse = Warehouse.objects.select_for_update().get(pk=serializer.instance.pk)
        new_capacity = serializer.validated_data.get('capacity')
        if new_capacity is not None:
            # Query freshest database sum under row lock
            current_total = warehouse.products.aggregate(total=Sum('quantity'))['total'] or 0
            if new_capacity < current_total:
                raise ValidationError({
                    "capacity": ["Sức chứa mới không được nhỏ hơn tổng số lượng sản phẩm hiện có trong kho."]
                })
        serializer.save()

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, pk=None):
        # Optimize query with select_related to prevent N+1 on warehouse relations
        warehouse = self.get_object()
        products = warehouse.products.select_related('warehouse').all()
        if 'page' in request.query_params:
            page = self.paginate_queryset(products)
            if page is not None:
                serializer = ProductSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
