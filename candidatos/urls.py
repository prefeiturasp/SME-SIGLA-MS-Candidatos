from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidatoViewSet

router = DefaultRouter()
router.register(r'candidatos', CandidatoViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
