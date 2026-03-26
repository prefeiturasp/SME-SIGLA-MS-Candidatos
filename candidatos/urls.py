from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidatoViewSet
from .views.habilitados import HabilitadosViewSet
from .views.parametrizacao import ParametrizacaoViewSet
from .views.reclassificados import ReclassificadosViewSet
from .views.eliminados import EliminadosViewSet
from .views.lotes import ConcursoCandidatosLoteViewSet

router = DefaultRouter()
router.register(r'candidatos', CandidatoViewSet)
router.register(r'habilitados', HabilitadosViewSet, basename='habilitados')
router.register(r'parametrizacao', ParametrizacaoViewSet, basename='parametrizacao')
router.register(r'reclassificados', ReclassificadosViewSet, basename='reclassificados')
router.register(r'eliminados', EliminadosViewSet, basename='eliminados')
router.register(r'lotes', ConcursoCandidatosLoteViewSet, basename='lotes')

urlpatterns = [
    path('', include(router.urls)),
]
