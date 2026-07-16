"""Módulo urls."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ParametrizacaoViewSet

router = DefaultRouter()
router.register(
    r"parametrizacao", ParametrizacaoViewSet, basename="parametrizacao"
)

urlpatterns = [
    path("", include(router.urls)),
]
