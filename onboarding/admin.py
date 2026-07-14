from django.contrib import admin
from .models import PerfilImportanciaFactor, HistorialImportancia


@admin.register(PerfilImportanciaFactor)
class PerfilImportanciaFactorAdmin(admin.ModelAdmin):
    list_display = ("empresa", "factor", "importancia", "actualizado_en")
    list_filter = ("empresa", "importancia")


@admin.register(HistorialImportancia)
class HistorialImportanciaAdmin(admin.ModelAdmin):
    list_display = ("empresa", "factor", "valor_anterior", "valor_nuevo", "fecha")
    list_filter = ("empresa",)
    readonly_fields = [f.name for f in HistorialImportancia._meta.fields]