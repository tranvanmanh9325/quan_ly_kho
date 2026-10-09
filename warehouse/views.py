from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Warehouse, Product
from .serializers import (
    WarehouseSerializer,
    ProductSerializer,
    StockAdjustmentSerializer,
    UserRegisterSerializer,
    UserLoginSerializer
)


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

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, pk=None):
        # Fetch all products belonging to a specific warehouse
        warehouse = self.get_object()
        products = warehouse.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            # Re-raise Django validation error as DRF ValidationError to return HTTP 400
            from rest_framework.exceptions import ValidationError
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)

    @action(detail=True, methods=['post'], url_path='adjust-stock')
    def adjust_stock(self, request, pk=None):
        """
        Custom business logic action for importing or exporting stock.
        """
        product = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']
        qty = serializer.validated_data['quantity']
        note = serializer.validated_data.get('note', '')

        if action_type == 'EXPORT':
            if product.quantity < qty:
                return Response(
                    {
                        "error": "BAD_REQUEST",
                        "message": f"Số lượng tồn kho không đủ để xuất! Hiện tại chỉ còn {product.quantity}, yêu cầu xuất {qty}."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            product.quantity -= qty
        elif action_type == 'IMPORT':
            product.quantity += qty

        try:
            product.save()
        except DjangoValidationError as exc:
            return Response(
                {
                    "error": "BAD_REQUEST",
                    "message": exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
                },
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


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Đăng ký tài khoản thành công!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "token": token.key
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Đăng nhập thành công!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "token": token.key
            },
            status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            },
            status=status.HTTP_200_OK
        )
