# Precarga el término de búsqueda en inglés (para Scopus) de los 18
# factores originales de GUIOSAD, igual de patrón que
# 0004_backfill_importancia_base. Sin esto, catalog.services buscaría en
# Scopus el nombre en español tal cual, que casi siempre da muy pocos
# resultados en una base bibliográfica mayormente en inglés.

from django.db import migrations

TERMINO_EN_POR_FACTOR = {
    "Compatibilidad": "Compatibility",
    "Personalización": "Customization",
    "Prueba": "Testability",
    "Fiabilidad": "Reliability",
    "Reusabilidad": "Reusability",
    "Usabilidad": "Usability",
    "Mantenibilidad": "Maintainability",
    "Portabilidad": "Portability",
    "Documentación": "Documentation",
    "Formación": "Training",
    "Tiempo de adopción": "Adoption time",
    "Casos de estudio de adopción FLOSS": "FLOSS adoption case studies",
    "Centralidad de la tecnología de la información": "IT centrality",
    "Apoyo de la alta dirección": "Top management support",
    "Bloqueo de proveedores": "Vendor lock-in",
    "Soporte": "Support",
    "Actitud hacia el cambio": "Attitude toward change",
    "Coste total de propiedad": "Total cost of ownership",
}


def backfill(apps, schema_editor):
    Factor = apps.get_model("catalog", "Factor")
    for nombre, termino_en in TERMINO_EN_POR_FACTOR.items():
        Factor.objects.filter(nombre=nombre).update(termino_busqueda_en=termino_en)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_factor_termino_busqueda_en_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
