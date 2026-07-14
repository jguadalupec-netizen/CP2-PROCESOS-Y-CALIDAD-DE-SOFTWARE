from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empresa, Usuario


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sector", "tamano", "cuestionario_completado", "fecha_registro")
    list_filter = ("sector", "tamano", "cuestionario_completado")
    search_fields = ("nombre",)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("GUIOS Pro+", {"fields": ("empresa", "rol")}),
    )
    list_display = ("username", "email", "empresa", "rol", "is_staff")
