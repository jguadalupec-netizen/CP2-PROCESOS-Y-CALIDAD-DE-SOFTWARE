from django.contrib.auth.models import AbstractUser
from django.db import models


class Empresa(models.Model):
    """
    Representa a la organización que usa GUIOS Pro+ para evaluar software.
    """
    SECTOR_CHOICES = [
        ("tecnologico", "Tecnológico"),
        ("financiero", "Financiero"),
        ("salud", "Salud"),
        ("educacion", "Educación"),
        ("gobierno", "Gobierno"),
        ("otro", "Otro"),
    ]

    TAMANO_CHOICES = [
        ("micro", "Microempresa (1-9 empleados)"),
        ("pequena", "Pequeña (10-49 empleados)"),
        ("mediana", "Mediana (50-249 empleados)"),
        ("grande", "Grande (250+ empleados)"),
    ]

    nombre = models.CharField(max_length=150)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default="otro")
    tamano = models.CharField(max_length=20, choices=TAMANO_CHOICES, default="pequena")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # Bandera para saber si ya completó el cuestionario inicial de importancia
    cuestionario_completado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """
    Usuario del sistema. Extiende el modelo base de Django para
    asociarlo a una Empresa y permitir roles (decisor/administrador).
    """
    ROL_CHOICES = [
        ("decisor", "Decisor"),
        ("administrador", "Administrador"),
    ]

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="usuarios",
        null=True, blank=True
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="decisor")

    def __str__(self):
        return self.username
