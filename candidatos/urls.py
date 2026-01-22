from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidatoViewSet
from .views.habilitados import HabilitadosViewSet
from .views.parametrizacao import ParametrizacaoViewSet

router = DefaultRouter()
router.register(r'candidatos', CandidatoViewSet)
router.register(r'habilitados', HabilitadosViewSet, basename='habilitados')
router.register(r'parametrizacao', ParametrizacaoViewSet, basename='parametrizacao')

urlpatterns = [
    path('', include(router.urls)),
]
