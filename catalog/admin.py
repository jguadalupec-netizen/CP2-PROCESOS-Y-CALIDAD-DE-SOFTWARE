from django.contrib import admin
from .models import Dimension, Factor, Subfactor


class SubfactorInline(admin.TabularInline):
    model = Subfactor
    extra = 1


@admin.register(Dimension)
class DimensionAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "dimension", "alcance", "activo")
    list_filter = ("dimension", "alcance", "activo")
    search_fields = ("nombre",)
    inlines = [SubfactorInline]


@admin.register(Subfactor)
class SubfactorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "factor", "activo")
    list_filter = ("factor__dimension", "activo")
