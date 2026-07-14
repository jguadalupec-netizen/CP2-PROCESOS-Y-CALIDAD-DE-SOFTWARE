from django.urls import path
from . import views

app_name = "evaluations"

urlpatterns = [
    path("nueva/", views.iniciar_evaluacion, name="iniciar"),
    path("<int:pk>/paso1/", views.paso1_factores, name="paso1"),
    path("<int:pk>/paso2/", views.paso2_subfactores, name="paso2"),
]
