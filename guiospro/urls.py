from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("accounts.urls")),
    path("catalogo/", include("catalog.urls")),
    path("evaluaciones/", include("evaluations.urls")),
    path("recomendaciones/", include("recommendations.urls")),
    path("", include("dashboard.urls")),
]
