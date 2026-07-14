# Backfill de importancia_base para factores ya cargados por
# cargar_catalogo antes de que este campo existiera, usando los mismos
# valores "Sugerida" de data/factors.csv.

from django.db import migrations

SUGERIDA_POR_FACTOR = {
    "Compatibilidad": 3,
    "Personalización": 3,
    "Prueba": 3,
    "Fiabilidad": 3,
    "Reusabilidad": 2,
    "Usabilidad": 3,
    "Mantenibilidad": 3,
    "Portabilidad": 2,
    "Documentación": 2,
    "Formación": 3,
    "Tiempo de adopción": 2,
    "Casos de estudio de adopción FLOSS": 2,
    "Centralidad de la tecnología de la información": 2,
    "Apoyo de la alta dirección": 2,
    "Bloqueo de proveedores": 2,
    "Soporte": 3,
    "Actitud hacia el cambio": 2,
    "Coste total de propiedad": 3,
}


def backfill(apps, schema_editor):
    Factor = apps.get_model("catalog", "Factor")
    for nombre, sugerida in SUGERIDA_POR_FACTOR.items():
        Factor.objects.filter(nombre=nombre).update(importancia_base=sugerida)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_factor_importancia_base"),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
