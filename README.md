# GUIOS Pro+

Migración a Django del sistema GUIOSAD (originalmente Flexx + pandas)
para el análisis y recomendación de adopción de software FLOSS,
mediante un análisis FODA ponderado por factores y subfactores.

## Apps del proyecto

- **accounts**: `Usuario` (custom, basado en `AbstractUser`) y `Empresa`, con roles decisor/administrador.
- **catalog**: `Dimension`, `Factor` y `Subfactor` — catálogo maestro editable desde
  **Administración de factores** (alta/edición/baja lógica, gestión de subfactores).
- **onboarding**: cuestionario inicial de importancia por empresa (`PerfilImportanciaFactor`),
  con historial de cambios (`HistorialImportancia`). Reemplaza la "Importancia Sugerida"
  fija del sistema original; es editable en cualquier momento.
- **evaluations**: `SoftwareEvaluado`, `Evaluacion`, `EvaluacionFactor`, `EvaluacionSubfactor`.
  Paso 1 (factores relevantes) y Paso 2 (evaluación de subfactores). Lógica de
  relevancia/ponderación en `services.py`.
- **recommendations**: `Recomendacion` — clasificación FODA y dictamen final (Niveles A/B/C)
  en el Paso 3, portados desde `main.py`/`MATRIZ_RECOMENDACION_GUIOSAD_2021.xlsx` originales.
- **dashboard**: pantalla principal con KPIs, evaluación en curso (stepper de pasos),
  distribución FODA acumulada y últimas evaluaciones.

## Cómo correr el proyecto

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Variables de entorno: copia la plantilla y ajusta si hace falta
cp .env.example .env            # Windows: copy .env.example .env

python manage.py migrate
python manage.py createsuperuser

# Carga el catálogo inicial de Dimensiones/Factores/Subfactores
# desde los CSV originales de GUIOSAD (data/guiosad_data.csv y data/factors.csv)
python manage.py cargar_catalogo

python manage.py runserver
```

Luego entra a `http://127.0.0.1:8000/` — la primera vez que una empresa
inicia sesión, el sistema la manda automáticamente al cuestionario de
importancia antes de dejarla evaluar software.

`http://127.0.0.1:8000/admin/` sigue disponible para administración
técnica de datos (usuarios, empresas, etc.) con la cuenta de
`createsuperuser`.

## Variables de entorno

El proyecto lee `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` desde un archivo
`.env` (no versionado — ver `.env.example` como plantilla). Genera una
clave propia para cada entorno con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Pendiente

- Exportar el reporte del Paso 3 en PDF real (`recommendations.views.exportar_reporte`
  hoy solo re-renderiza la misma pantalla; hay `weasyprint` en `requirements.txt`
  para implementarlo).
- Recuperación de contraseña ("Olvidé mi contraseña" en el login es solo visual
  por ahora) e inicio de sesión con Google/Microsoft (botones deshabilitados).
- Tests automatizados (los `tests.py` de cada app están vacíos todavía).
