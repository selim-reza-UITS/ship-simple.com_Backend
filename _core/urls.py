# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Make sure to import CalculatorViewSet
from _core.api.views import (
    ShippingRateViewSet, 
    CategoryViewSet, 
    ShippingConfigViewSet, 
    CalculatorViewSet,
    AdminLoginView
)

router = DefaultRouter()
router.register(r'shipping-rates', ShippingRateViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'shipping-config', ShippingConfigViewSet)
# Register the calculator
router.register(r'calculator', CalculatorViewSet, basename='calculator')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', AdminLoginView.as_view(), name='admin_login'),
]