from django.urls import path
from . import views

app_name = "onboarding"

urlpatterns = [
    path("cuestionario/", views.cuestionario_importancia, name="cuestionario"),
    path("cuestionario/editar/", views.editar_importancia, name="editar_importancia"),
]