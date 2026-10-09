from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        "project": "Hệ thống Quản lý kho bãi API",
        "version": "v1",
        "documentation": {
            "auth": {
                "register": "/api/v1/auth/register/",
                "login": "/api/v1/auth/login/",
                "profile": "/api/v1/auth/me/"
            },
            "warehouses": "/api/v1/warehouses/",
            "products": "/api/v1/products/"
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('warehouse.urls')),
    path('', api_root, name='api-root'),
]
