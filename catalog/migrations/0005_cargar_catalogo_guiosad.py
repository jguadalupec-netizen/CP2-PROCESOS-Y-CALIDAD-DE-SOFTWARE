# Data migration: carga el catálogo original de GUIOSAD (Dimensión /
# Factor / Subfactor) para que "python manage.py migrate" deje el
# catálogo listo en cualquier entorno nuevo, sin depender de correr
# a mano "python manage.py cargar_catalogo".
#
# Los datos son los mismos de data/guiosad_data.csv (Dimensión, Factor,
# Subfactor) y data/factors.csv (Factor, Sugerida, Alcance), que a su vez
# son los que usaba guiosad.py/main.py del prototipo GUIOSAD original.
# Se embeben aquí (en vez de leer los CSV en tiempo de migración) para
# que la migración sea autocontenida y reproducible, siguiendo el mismo
# patrón que 0004_backfill_importancia_base.
#
# Es idempotente (get_or_create): si el catálogo ya fue cargado antes
# con "cargar_catalogo" (mismos nombres), no se duplica nada.

from django.db import migrations

CATALOGO = {
    "Tecnológica": {
        "Compatibilidad": {
            "alcance": "externo",
            "importancia_base": 3,
            "subfactores": [
                "Una empresa proporciona una infraestructura de nube lista para usar para este software",
                "Los programas informáticos pueden exportar formatos propietarios",
                "El software interactúa y se integra con el software propietario existente",
                "El software está certificado para operar en su nicho de mercado",
                "El software es compatible con los casos de uso y las funcionalidades más comunes",
                "El software es compatible con múltiples componentes de hardware",
                "El software utiliza formatos estándar",
                "El software es compatible con varios sistemas operativos diferentes (el software es multiplataforma)",
            ],
        },
        "Personalización": {
            "alcance": "externo",
            "importancia_base": 3,
            "subfactores": [
                "El acceso al código fuente es un incentivo para la organización",
                "El software se puede ampliar fácilmente para satisfacer las necesidades de la organización modificando el código fuente",
                "Las innovaciones se introducen en el software a un ritmo rápido",
                "El software es fácil de personalizar sin necesidad de modificar el códigofuente",
                "El software soporta nuevas funciones a través de módulos (el software es modular)",
                "Hay un repositorio público de extensiones para este software",
            ],
        },
        "Prueba": {
            "alcance": "externo",
            "importancia_base": 3,
            "subfactores": [
                "El software es fácil de desplegar y de probar",
            ],
        },
        "Fiabilidad": {
            "alcance": "externo",
            "importancia_base": 3,
            "subfactores": [
                "El software es fiable y estable",
                "El software tiene un buen historial en cuanto a errores de seguridad (el software es seguro)",
                "El software es más flexible que la solución propietaria",
                "El software es más confiable que la solución propietaria",
                "El programa proporciona una amplia variedad de funciones de control de acceso",
            ],
        },
        "Reusabilidad": {
            "alcance": "externo",
            "importancia_base": 2,
            "subfactores": [
                "La licencia permite extensiones propietarias",
                "El software se ofrece como una biblioteca / marco de trabajo",
            ],
        },
        "Usabilidad": {
            "alcance": "externo",
            "importancia_base": 3,
            "subfactores": [
                "El software proporciona una interfaz gráfica de usuario (GUI)",
                "El software es más fácil de usar que la alternativa propietaria",
                "El software es fácil de aprender",
                "El usuario está descontento con el software propietario",
            ],
        },
        "Mantenibilidad": {
            "alcance": "externo",
            "importancia_base": 3,
            "subfactores": [
                "El software es mantenido activamente por los desarrolladores",
            ],
        },
        "Portabilidad": {
            "alcance": "externo",
            "importancia_base": 2,
            "subfactores": [
                "Una versión de aplicación móvil de este software está disponible",
                "El software es una sistemas de administración de base de datos independiente",
            ],
        },
        "Documentación": {
            "alcance": "externo",
            "importancia_base": 2,
            "subfactores": [
                "El software está bien documentado",
                "La documentación de desarrollo cubre todas las características",
                "La documentación está disponible en múltiples formatos",
                "La documentación es fácil de entender",
                "La documentación está actualizada",
                "La documentación está escrita por escritores especializados (no desarrolladores)",
                "La documentación del software es de alta calidad",
                "El software viene con documentación de desarrollo",
                "El software viene con documentación de usuario",
                "La documentación del usuario cubre todas las características",
                "Los formatos de datos están bien documentados",
            ],
        },
    },
    "Organizacional": {
        "Formación": {
            "alcance": "interno",
            "importancia_base": 3,
            "subfactores": [
                "La adopción de este software permite a los usuarios mejorar las habilidades técnicas de TI",
                "El personal de la organización puede aprender fácilmente por sí mismo a utilizar este software",
                "El personal de la organización está capacitado para resolver problemas tecnológicos",
                "Los planes de entrenamiento de este software están disponibles",
            ],
        },
        "Tiempo de adopción": {
            "alcance": "interno",
            "importancia_base": 2,
            "subfactores": [
                "Los requisitos de instalación y despliegue del software son fáciles de cumplir",
                "El tiempo requerido para adoptar este software es bajo",
            ],
        },
        "Casos de estudio de adopción FLOSS": {
            "alcance": "externo",
            "importancia_base": 2,
            "subfactores": [
                "Hay informes públicos disponibles en Internet que describen el éxito de la adopción de este software",
            ],
        },
        "Centralidad de la tecnología de la información": {
            "alcance": "interno",
            "importancia_base": 2,
            "subfactores": [
                "La adopción de este software mejora el entorno de trabajo de los usuarios",
                "Centralizar la infraestructura de TI ayuda a acelerar la adopción de este software",
            ],
        },
        "Apoyo de la alta dirección": {
            "alcance": "interno",
            "importancia_base": 2,
            "subfactores": [
                "La alta dirección apoya la adopción exitosa de este software",
            ],
        },
        "Bloqueo de proveedores": {
            "alcance": "externo",
            "importancia_base": 2,
            "subfactores": [
                "El software reduce las dependencias de los proveedores en su entorno",
            ],
        },
        "Soporte": {
            "alcance": "ambos",
            "importancia_base": 3,
            "subfactores": [
                "El soporte de la comunidad para este software está disponible",
                "Soporte de expertos y consultores externos para consultas específicas está disponible",
                "El soporte comercial de este software está disponible 24/7/365",
                "Hay desarrolladores en su organización que saben cómo desarrollar este software",
                "Soporte comercial para la personalización de software está disponible",
                "Es fácil contratar personal informático en la comunidad que conozca este software",
            ],
        },
        "Actitud hacia el cambio": {
            "alcance": "interno",
            "importancia_base": 2,
            "subfactores": [
                "El personal de la organización muestra poca resistencia al cambio tecnológico",
                "El personal técnico encargado del despliegue y soporte en la organización respalda la adopción de este software",
            ],
        },
    },
    "Económica": {
        "Coste total de propiedad": {
            "alcance": "interno",
            "importancia_base": 3,
            "subfactores": [
                "Es poco probable que haya costos ocultos al adoptar este software",
                "La adopción de este software es menos costosa que la alternativa patentada",
            ],
        },
    },
}


def cargar_catalogo(apps, schema_editor):
    Dimension = apps.get_model("catalog", "Dimension")
    Factor = apps.get_model("catalog", "Factor")
    Subfactor = apps.get_model("catalog", "Subfactor")

    for dim_nombre, factores in CATALOGO.items():
        dimension, _ = Dimension.objects.get_or_create(nombre=dim_nombre)
        for factor_nombre, datos in factores.items():
            factor, _ = Factor.objects.get_or_create(
                nombre=factor_nombre,
                dimension=dimension,
                defaults={
                    "alcance": datos["alcance"],
                    "importancia_base": datos["importancia_base"],
                },
            )
            for subfactor_nombre in datos["subfactores"]:
                Subfactor.objects.get_or_create(nombre=subfactor_nombre, factor=factor)


def noop(apps, schema_editor):
    # No se revierte: borrar el catálogo en cascada eliminaría
    # evaluaciones ya realizadas por los factores/subfactores creados.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_backfill_importancia_base"),
    ]

    operations = [
        migrations.RunPython(cargar_catalogo, noop),
    ]
