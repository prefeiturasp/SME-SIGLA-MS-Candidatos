from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidatoViewSet
from .views.habilitados import HabilitadosViewSet
from .views.parametrizacao import ParametrizacaoAtualView

router = DefaultRouter()
router.register(r'candidatos', CandidatoViewSet)
router.register(r'habilitados', HabilitadosViewSet, basename='habilitados')


urlpatterns = [
    path('', include(router.urls)),
    path('parametrizacao/', ParametrizacaoAtualView.as_view(), name='parametrizacao-atual'),
]
