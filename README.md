# GUIOS Pro+

Migración a Django del sistema GUIOSAD (originalmente Flexx + pandas)
para el análisis y recomendación de adopción de software FLOSS,
mediante un análisis FODA ponderado por factores y subfactores.

## Apps del proyecto

- **accounts**: `Usuario` (custom, basado en `AbstractUser`) y `Empresa`, con roles decisor/administrador.
- **catalog**: `Dimension`, `Factor` y `Subfactor` — catálogo maestro editable desde
  **Administración de factores** (alta/edición/baja lógica, gestión de subfactores).
  El catálogo original de GUIOSAD (3 dimensiones, 18 factores, 61 subfactores) se
  carga solo con `migrate` vía una data migration (`catalog/migrations/0005_cargar_catalogo_guiosad.py`);
  el comando `python manage.py cargar_catalogo` sigue disponible por si necesitas
  recargar desde los CSV en `data/` (por ejemplo con `--reset`). También calcula
  la Importancia Sugerida (IS) de cada evaluación automáticamente combinando
  `Factor.importancia_base` con evidencia bibliográfica de Scopus
  (`catalog/services.py`) — ya no hay cuestionario de onboarding.
- **evaluations**: `SoftwareEvaluado`, `Evaluacion`, `EvaluacionFactor`, `EvaluacionSubfactor`.
  Paso 1 (factores relevantes) y Paso 2 (evaluación de subfactores). Lógica de
  relevancia/ponderación en `services.py`.
- **recommendations**: `Recomendacion` — clasificación FODA y dictamen final (Niveles A/B/C)
  en el Paso 3, portados desde `main.py`/`MATRIZ_RECOMENDACION_GUIOSAD_2021.xlsx` originales.
  El botón "Exportar reporte" genera un PDF real (vía `xhtml2pdf`) con el mismo
  contenido de la pantalla de resultado (`templates/recommendations/resultado_pdf.html`).
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

python manage.py runserver
```

Luego entra a `http://127.0.0.1:8000/` — ya no hay cuestionario inicial que
responder; cualquier empresa puede evaluar software desde el primer login.

`http://127.0.0.1:8000/admin/` sigue disponible para administración
técnica de datos (usuarios, empresas, etc.) con la cuenta de
`createsuperuser`.

> Si tu base de datos local es anterior a este cambio (tenía el cuestionario
> de onboarding cargado), corre `python manage.py migrate onboarding zero`
> **antes** de actualizar el código, para que Django elimine esas tablas en
> vez de dejarlas huérfanas.

## Variables de entorno

El proyecto lee `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` y `SCOPUS_API_KEY`
desde un archivo `.env` (no versionado — ver `.env.example` como plantilla).
Genera una clave propia para cada entorno con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`SCOPUS_API_KEY` es opcional: es la API key de Elsevier/Scopus usada por
`catalog.services.calcular_importancia_sugerida` para automatizar la
Importancia Sugerida (IS) de cada factor con evidencia bibliográfica. Si se
deja vacía, o Scopus falla/no responde a tiempo/no hay evidencia suficiente,
el sistema usa `Factor.importancia_base` tal cual (sin romper nada).

## Pendiente

- Recuperación de contraseña ("Olvidé mi contraseña" en el login es solo visual
  por ahora) e inicio de sesión con Google/Microsoft (botones deshabilitados).
- Tests automatizados (los `tests.py` de cada app están vacíos todavía).
