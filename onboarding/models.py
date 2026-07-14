from django.db import models
from django.conf import settings
from accounts.models import Empresa
from catalog.models import Factor


class PerfilImportanciaFactor(models.Model):
    """
    Respuesta de la empresa al cuestionario inicial: "¿qué tan importante
    es este factor para nosotros?". Sustituye a la 'Importancia Sugerida'
    fija de la versión original (factors.csv), y es editable en el tiempo.
    """
    NIVEL_CHOICES = [
        (1, "Irrelevante"),
        (2, "Opcional"),
        (3, "Importante"),
        (4, "Fundamental"),
    ]

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="perfil_importancia"
    )
    factor = models.ForeignKey(
        Factor, on_delete=models.CASCADE, related_name="perfiles_importancia"
    )
    importancia = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES, default=2)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Perfil de importancia por factor"
        verbose_name_plural = "Perfiles de importancia por factor"
        unique_together = ("empresa", "factor")

    def __str__(self):
        return f"{self.empresa} - {self.factor}: {self.get_importancia_display()}"


class HistorialImportancia(models.Model):
    """
    Bitácora de cambios al cuestionario, para trazabilidad y para
    poder mostrar en el análisis cómo evoluciona la percepción
    de importancia de la empresa a lo largo del tiempo.
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="historial_importancia")
    factor = models.ForeignKey(Factor, on_delete=models.CASCADE)
    valor_anterior = models.PositiveSmallIntegerField(null=True, blank=True)
    valor_nuevo = models.PositiveSmallIntegerField()
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de importancia"
        verbose_name_plural = "Historial de importancia"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.empresa} - {self.factor}: {self.valor_anterior} -> {self.valor_nuevo}"