# Ajuste de 3 términos de búsqueda (de los precargados en
# 0007_backfill_termino_busqueda_en) que en la práctica devolvían muy pocos
# resultados en Scopus por ser traducciones demasiado literales/poco usadas
# en la literatura indexada. Verificado contra la API real:
#   "Attitude toward change"      -> 0 resultados
#   "resistance to change"        -> 10 resultados
#   "FLOSS adoption case studies" -> 0 resultados
#   "case studies"                -> 4152 resultados
#   "Adoption time"                -> 0 resultados
#   "implementation time"          -> 13 resultados
#
# "IT centrality" (Centralidad de la tecnología de la información) se probó
# con varias alternativas y todas dieron 0 -- se deja igual; ese factor
# caerá al fallback (importancia_base) con evidencia insuficiente, lo cual
# es el comportamiento esperado, no un error.

from django.db import migrations

AJUSTES = {
    "Actitud hacia el cambio": "resistance to change",
    "Casos de estudio de adopción FLOSS": "case studies",
    "Tiempo de adopción": "implementation time",
}


def ajustar(apps, schema_editor):
    Factor = apps.get_model("catalog", "Factor")
    for nombre, termino_en in AJUSTES.items():
        Factor.objects.filter(nombre=nombre).update(termino_busqueda_en=termino_en)


def revertir(apps, schema_editor):
    Factor = apps.get_model("catalog", "Factor")
    Factor.objects.filter(nombre="Actitud hacia el cambio").update(termino_busqueda_en="Attitude toward change")
    Factor.objects.filter(nombre="Casos de estudio de adopción FLOSS").update(termino_busqueda_en="FLOSS adoption case studies")
    Factor.objects.filter(nombre="Tiempo de adopción").update(termino_busqueda_en="Adoption time")


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_backfill_termino_busqueda_en"),
    ]

    operations = [
        migrations.RunPython(ajustar, revertir),
    ]
