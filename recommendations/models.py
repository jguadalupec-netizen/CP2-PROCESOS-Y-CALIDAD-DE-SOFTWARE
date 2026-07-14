from django.db import models
from evaluations.models import Evaluacion


class Recomendacion(models.Model):
    """
    Resultado final (Paso 3) de una Evaluacion: nivel de recomendación
    (A/B/C) calculado por recommendations.services a partir de la
    matriz de decisión (ver MATRIZ_RECOMENDACION_GUIOSAD_2021.xlsx).
    """
    NIVEL_CHOICES = [
        ("A", "No es posible adoptar"),
        ("B", "Es posible adoptar con reservas"),
        ("C", "Adoptar"),
    ]

    evaluacion = models.OneToOneField(
        Evaluacion, on_delete=models.CASCADE, related_name="recomendacion"
    )
    nivel = models.CharField(max_length=1, choices=NIVEL_CHOICES)
    texto = models.TextField()

    # Promedio (0-5) de ponderacion_media de los factores relevantes e
    # incluidos de la evaluación. Se usa como "Puntaje" resumen en el
    # Dashboard y en el listado de evaluaciones.
    puntaje_promedio = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    total_fortalezas = models.PositiveSmallIntegerField(default=0)
    total_oportunidades = models.PositiveSmallIntegerField(default=0)
    total_debilidades = models.PositiveSmallIntegerField(default=0)
    total_amenazas = models.PositiveSmallIntegerField(default=0)

    generado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recomendación"
        verbose_name_plural = "Recomendaciones"

    def __str__(self):
        return f"Recomendación {self.nivel} - {self.evaluacion}"
