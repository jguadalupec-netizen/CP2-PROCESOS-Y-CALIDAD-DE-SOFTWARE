from django.db import models
from django.conf import settings
from accounts.models import Empresa
from catalog.models import Factor, Subfactor


class SoftwareEvaluado(models.Model):
    """
    El software (candidato FLOSS u otro) que la empresa está evaluando.
    """
    nombre = models.CharField(max_length=150)
    version = models.CharField(max_length=50, blank=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="softwares_evaluados"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Software evaluado"
        verbose_name_plural = "Softwares evaluados"

    def __str__(self):
        return f"{self.nombre} {self.version}".strip()


class Evaluacion(models.Model):
    """
    Una evaluación completa (Pasos 1-2-3) de un SoftwareEvaluado.
    """
    ESTADO_CHOICES = [
        ("en_progreso", "En progreso"),
        ("completada", "Completada"),
    ]
    PASO_CHOICES = [
        (1, "Paso 1: Factores relevantes"),
        (2, "Paso 2: Subfactores"),
        (3, "Paso 3: Resultado"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="evaluaciones")
    software = models.ForeignKey(SoftwareEvaluado, on_delete=models.CASCADE, related_name="evaluaciones")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    paso_actual = models.PositiveSmallIntegerField(choices=PASO_CHOICES, default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="en_progreso")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"Evaluación de {self.software} - {self.empresa}"


class EvaluacionFactor(models.Model):
    """
    Evaluación de UN factor dentro de UNA evaluación (Paso 1).

    'importancia_sugerida_snapshot' congela el valor del cuestionario
    de la empresa (onboarding.PerfilImportanciaFactor) al momento de
    iniciar la evaluación, para que cambios futuros al cuestionario
    no alteren evaluaciones ya realizadas.
    """
    NIVEL_CHOICES = [
        (1, "Irrelevante"),
        (2, "Opcional"),
        (3, "Importante"),
        (4, "Fundamental"),
    ]
    ALCANCE_CHOICES = [
        ("interno", "Interno"),
        ("externo", "Externo"),
    ]

    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name="factores")
    factor = models.ForeignKey(Factor, on_delete=models.CASCADE, related_name="evaluaciones_factor")

    importancia_sugerida_snapshot = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES)
    importancia_decisor = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES, default=1)
    importancia_relativa = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES, null=True, blank=True)

    # Permite al decisor excluir un factor puntual de ESTA evaluación
    # (ej. "no aplica para este software"), sin afectar el catálogo ni
    # otras evaluaciones. Un factor con incluido=False no entra en el
    # cálculo de la recomendación final (Paso 3), aunque haya salido
    # relevante.
    incluido = models.BooleanField(default=True, verbose_name="Incluido en esta evaluación")

    alcance = models.CharField(max_length=10, choices=ALCANCE_CHOICES, default="interno")
    relevante = models.BooleanField(default=False)

    # Resultado del Paso 2, calculado a partir de EvaluacionSubfactor
    ponderacion_media = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    clasificacion_foda = models.CharField(max_length=20, blank=True)  # Fortaleza/Oportunidad/Debilidad/Amenaza

    class Meta:
        verbose_name = "Factor evaluado"
        verbose_name_plural = "Factores evaluados"
        unique_together = ("evaluacion", "factor")

    def __str__(self):
        return f"{self.factor} en {self.evaluacion}"


class EvaluacionSubfactor(models.Model):
    """
    Evaluación de cumplimiento de UN subfactor (Paso 2).
    """
    NIVEL_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    evaluacion_factor = models.ForeignKey(
        EvaluacionFactor, on_delete=models.CASCADE, related_name="subfactores"
    )
    subfactor = models.ForeignKey(Subfactor, on_delete=models.CASCADE, related_name="evaluaciones_subfactor")
    valor_cumplimiento = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES, default=1)

    class Meta:
        verbose_name = "Subfactor evaluado"
        verbose_name_plural = "Subfactores evaluados"
        unique_together = ("evaluacion_factor", "subfactor")

    def __str__(self):
        return f"{self.subfactor} = {self.get_valor_cumplimiento_display()}"