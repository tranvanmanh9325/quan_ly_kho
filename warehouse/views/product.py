from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from warehouse.models import Product, Warehouse
from warehouse.serializers import ProductSerializer, StockAdjustmentSerializer
from warehouse.services import (
    adjust_product_stock,
    InsufficientStockError,
    StockCapacityError
)


class DjangoValidationErrorMixin:
    """
    Mixin for DRF ViewSets to cleanly translate Django Model ValidationErrors
    into DRF ValidationErrors (HTTP 400 Bad Request), adhering to DRY.
    """
    def save_with_model_validation(self, serializer):
        try:
            return serializer.save()
        except DjangoValidationError as exc:
            detail = exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
            raise ValidationError(detail)


class ProductViewSet(DjangoValidationErrorMixin, viewsets.ModelViewSet):
    """
    CRUD API for Products in Warehouses.
    GET /api/v1/products/ -> 200 OK (List with filtering)
    POST /api/v1/products/ -> 201 Created / 400 Bad Request
    GET /api/v1/products/{id}/ -> 200 OK / 404 Not Found
    PUT /api/v1/products/{id}/ -> 200 OK / 400 Bad Request
    DELETE /api/v1/products/{id}/ -> 204 No Content
    POST /api/v1/products/{id}/adjust-stock/ -> 200 OK / 400 Bad Request
    """
    queryset = Product.objects.select_related('warehouse').all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse_id = self.request.query_params.get('warehouse')
        category = self.request.query_params.get('category')
        stock_status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if category:
            queryset = queryset.filter(category__iexact=category)
        if stock_status:
            queryset = queryset.filter(status=stock_status)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        # Lock parent warehouse row to serialize concurrent stock creation against capacity
        warehouse = serializer.validated_data.get('warehouse')
        if warehouse:
            Warehouse.objects.select_for_update().get(pk=warehouse.pk)
        self.save_with_model_validation(serializer)

    @transaction.atomic
    def perform_update(self, serializer):
        # Lock affected warehouse(s) and product row to protect capacity invariant and prevent lost updates
        instance = serializer.instance
        target_warehouse = serializer.validated_data.get('warehouse', instance.warehouse)
        if target_warehouse.pk != instance.warehouse_id:
            # Deterministic lock ordering on warehouse IDs to eliminate any possibility of deadlock
            for wh_id in sorted([instance.warehouse_id, target_warehouse.pk]):
                Warehouse.objects.select_for_update().get(pk=wh_id)
        else:
            Warehouse.objects.select_for_update().get(pk=instance.warehouse_id)

        # Lock product row
        Product.objects.select_for_update().get(pk=instance.pk)
        self.save_with_model_validation(serializer)

    @action(detail=True, methods=['post'], url_path='adjust-stock')
    def adjust_stock(self, request, pk=None):
        """
        Custom business logic action for importing or exporting stock.
        Delegates core business adjustment logic to stock_service.
        """
        product = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']
        qty = serializer.validated_data['quantity']
        note = serializer.validated_data.get('note', '')

        try:
            product = adjust_product_stock(product, action_type, qty)
        except (InsufficientStockError, StockCapacityError, ValidationError) as exc:
            return Response(
                exc.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_serializer = ProductSerializer(product)
        return Response(
            {
                "message": f"Thao tác {action_type} thành công {qty} sản phẩm.",
                "note": note,
                "product": updated_serializer.data
            },
            status=status.HTTP_200_OK
        )
