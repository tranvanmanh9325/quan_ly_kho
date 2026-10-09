from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet,
    ProductViewSet,
    RegisterView,
    LoginView,
    UserProfileView
)

# Use DefaultRouter to automatically generate RESTful endpoints
router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/me/', UserProfileView.as_view(), name='auth-me'),
    
    # ViewSet CRUD endpoints
    path('', include(router.urls)),
]
