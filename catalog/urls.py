from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("administracion/", views.lista_factores, name="administracion"),
    path("factores/nuevo/", views.crear_factor, name="crear_factor"),
    path("factores/<int:pk>/editar/", views.editar_factor, name="editar_factor"),
    path("factores/<int:pk>/eliminar/", views.eliminar_factor, name="eliminar_factor"),
]
