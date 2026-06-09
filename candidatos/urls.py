"""Módulo urls."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CandidatoViewSet
from .views.eliminados import EliminadosViewSet
from .views.habilitados import HabilitadosViewSet
from .views.parametrizacao import ParametrizacaoViewSet
from .views.reclassificados import ReclassificadosViewSet

router = DefaultRouter()
router.register(r"candidatos", CandidatoViewSet)
router.register(r"habilitados", HabilitadosViewSet, basename="habilitados")
router.register(
    r"parametrizacao", ParametrizacaoViewSet, basename="parametrizacao"
)
router.register(
    r"reclassificados", ReclassificadosViewSet, basename="reclassificados"
)
router.register(r"eliminados", EliminadosViewSet, basename="eliminados")

urlpatterns = [
    path("", include(router.urls)),
]
