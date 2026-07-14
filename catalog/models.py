from django.db import models


class Dimension(models.Model):
    """
    Agrupador de más alto nivel: Tecnológica, Organizacional, Económica, etc.
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Dimensión"
        verbose_name_plural = "Dimensiones"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Factor(models.Model):
    """
    Factor evaluable dentro de una dimensión (ej. Compatibilidad, Seguridad).
    Editable desde el panel de Administración (Pantalla 7).
    """
    ALCANCE_CHOICES = [
        ("interno", "Interno"),
        ("externo", "Externo"),
        ("ambos", "Ambos"),
    ]
    IMPORTANCIA_CHOICES = [
        (1, "Irrelevante"),
        (2, "Opcional"),
        (3, "Importante"),
        (4, "Fundamental"),
    ]

    nombre = models.CharField(max_length=150)
    dimension = models.ForeignKey(
        Dimension, on_delete=models.CASCADE, related_name="factores"
    )
    importancia_base = models.PositiveSmallIntegerField(
        choices=IMPORTANCIA_CHOICES,
        default=2,
        verbose_name="Importancia sugerida",
        help_text=(
            "Valor de partida del catálogo (equivalente a 'Sugerida' en factors.csv). "
            "Se usa como respuesta por defecto del cuestionario de importancia para "
            "empresas/factores nuevos, antes de que el decisor la ajuste."
        ),
    )
    alcance = models.CharField(max_length=10, choices=ALCANCE_CHOICES, default="interno")
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Factor"
        verbose_name_plural = "Factores"
        ordering = ["dimension", "nombre"]
        unique_together = ("nombre", "dimension")

    def __str__(self):
        return f"{self.nombre} ({self.dimension})"


class Subfactor(models.Model):
    """
    Criterio específico que compone a un Factor.
    """
    nombre = models.CharField(max_length=255)
    factor = models.ForeignKey(
        Factor, on_delete=models.CASCADE, related_name="subfactores"
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Subfactor"
        verbose_name_plural = "Subfactores"
        ordering = ["factor", "id"]

    def __str__(self):
        return self.nombre
