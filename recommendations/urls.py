from django.urls import path
from . import views

app_name = "recommendations"

urlpatterns = [
    path("<int:evaluacion_id>/resultado/", views.resultado, name="resultado"),
    path("<int:evaluacion_id>/exportar/", views.exportar_reporte, name="exportar"),
]
