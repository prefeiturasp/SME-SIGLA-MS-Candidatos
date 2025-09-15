"""
URL configuration for candidatos project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def healthcheck(_request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('candidatos.urls')),
    path('', healthcheck, name='healthcheck'),
]
