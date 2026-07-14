from django.contrib import admin
from .models import SoftwareEvaluado, Evaluacion, EvaluacionFactor, EvaluacionSubfactor


class EvaluacionSubfactorInline(admin.TabularInline):
    model = EvaluacionSubfactor
    extra = 0


class EvaluacionFactorInline(admin.TabularInline):
    model = EvaluacionFactor
    extra = 0
    show_change_link = True


@admin.register(SoftwareEvaluado)
class SoftwareEvaluadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "version", "empresa", "creado_en")


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ("software", "empresa", "paso_actual", "estado", "fecha_inicio")
    list_filter = ("estado", "paso_actual", "empresa")
    inlines = [EvaluacionFactorInline]


@admin.register(EvaluacionFactor)
class EvaluacionFactorAdmin(admin.ModelAdmin):
    list_display = ("evaluacion", "factor", "importancia_relativa", "relevante", "clasificacion_foda")
    list_filter = ("relevante", "clasificacion_foda", "alcance")
    inlines = [EvaluacionSubfactorInline]
