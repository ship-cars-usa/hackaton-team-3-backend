from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from app import views

router = routers.DefaultRouter()
router.register(r"", views.DamageInspectionView, basename="app")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(router.urls)),
]
