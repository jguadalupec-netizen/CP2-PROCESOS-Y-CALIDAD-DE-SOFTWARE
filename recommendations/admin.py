from django.contrib import admin
from .models import Recomendacion


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ("evaluacion", "nivel", "total_fortalezas", "total_oportunidades",
                     "total_debilidades", "total_amenazas", "generado_en")
    list_filter = ("nivel",)
