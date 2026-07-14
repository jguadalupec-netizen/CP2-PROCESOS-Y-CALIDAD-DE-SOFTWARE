"""
Comando de carga inicial del catálogo (Dimensión / Factor / Subfactor)
a partir de los CSV originales del sistema GUIOSAD (guiosad_data.csv
y factors.csv), separados por tabulaciones, tal como los leía
guiosad.py con pandas (sep="\t").

Uso:
    python manage.py cargar_catalogo
    python manage.py cargar_catalogo --data-file otra_ruta/guiosad_data.csv --factors-file otra_ruta/factors.csv
    python manage.py cargar_catalogo --reset   # borra el catálogo actual antes de cargar
"""
import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Dimension, Factor, Subfactor

ALCANCE_MAP = {
    "Interno": "interno",
    "Externo": "externo",
    "Ambos": "ambos",
}


class Command(BaseCommand):
    help = "Carga el catálogo inicial de Dimensiones, Factores y Subfactores desde los CSV originales de GUIOSAD."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-file",
            default=str(settings.BASE_DIR / "data" / "guiosad_data.csv"),
            help="Ruta a guiosad_data.csv (Dimensión, Factor, Subfactor).",
        )
        parser.add_argument(
            "--factors-file",
            default=str(settings.BASE_DIR / "data" / "factors.csv"),
            help="Ruta a factors.csv (Factor, Sugerida, Alcance).",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina Dimensiones/Factores/Subfactores existentes antes de cargar.",
        )

    def handle(self, *args, **options):
        data_path = Path(options["data_file"])
        factors_path = Path(options["factors_file"])

        if not data_path.exists():
            raise CommandError(f"No se encontró el archivo: {data_path}")
        if not factors_path.exists():
            raise CommandError(f"No se encontró el archivo: {factors_path}")

        if options["reset"]:
            self.stdout.write(self.style.WARNING("Eliminando catálogo existente..."))
            Subfactor.objects.all().delete()
            Factor.objects.all().delete()
            Dimension.objects.all().delete()

        # --- Paso 1: alcance e importancia sugerida por factor (factors.csv) ---
        alcance_por_factor = {}
        importancia_por_factor = {}
        with open(factors_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                nombre = row["Factor"].strip()
                alcance_txt = row["Alcance"].strip()
                alcance_por_factor[nombre] = ALCANCE_MAP.get(alcance_txt, "interno")
                try:
                    importancia_por_factor[nombre] = int(row["Sugerida"].strip())
                except (KeyError, ValueError):
                    pass

        # --- Paso 2: Dimensión -> Factor -> Subfactor (guiosad_data.csv) ---
        dimensiones_creadas = {}
        factores_creados = {}
        total_subfactores = 0

        with transaction.atomic():
            with open(data_path, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    dim_nombre = row["Dimensión"].strip()
                    factor_nombre = row["Factor"].strip()
                    subfactor_nombre = row["Subfactor"].strip()

                    dimension = dimensiones_creadas.get(dim_nombre)
                    if dimension is None:
                        dimension, _ = Dimension.objects.get_or_create(nombre=dim_nombre)
                        dimensiones_creadas[dim_nombre] = dimension

                    factor_key = (dim_nombre, factor_nombre)
                    factor = factores_creados.get(factor_key)
                    if factor is None:
                        alcance = alcance_por_factor.get(factor_nombre, "interno")
                        importancia_base = importancia_por_factor.get(factor_nombre, 2)
                        factor, _ = Factor.objects.get_or_create(
                            nombre=factor_nombre,
                            dimension=dimension,
                            defaults={"alcance": alcance, "importancia_base": importancia_base},
                        )
                        factores_creados[factor_key] = factor

                    _, created = Subfactor.objects.get_or_create(
                        nombre=subfactor_nombre,
                        factor=factor,
                    )
                    if created:
                        total_subfactores += 1

        self.stdout.write(self.style.SUCCESS(
            f"Catálogo cargado: {len(dimensiones_creadas)} dimensiones, "
            f"{len(factores_creados)} factores, {total_subfactores} subfactores."
        ))
