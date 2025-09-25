from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from candidatos.views import SwaggerFromFileView

def healthcheck(_request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('candidatos.urls')),
    path('api/docs/', SwaggerFromFileView.as_view(), name='swagger-ui'),
    path('', healthcheck, name='healthcheck'),
]
