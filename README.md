# GUIOS Pro+

Migración a Django del sistema GUIOSAD (originalmente flexx + pandas),
para la evaluación y recomendación de adopción de software FLOSS.

## Apps del proyecto

- **accounts**: Usuario (custom) y Empresa, autenticación.
- **catalog**: Dimensión, Factor y Subfactor (editable desde Administración).
- **onboarding**: cuestionario de importancia inicial por empresa
  (reemplaza la "Importancia Sugerida" fija del sistema original) +
  historial de cambios.
- **evaluations**: SoftwareEvaluado, Evaluacion, EvaluacionFactor,
  EvaluacionSubfactor. Lógica de relevancia y ponderación en `services.py`.
- **recommendations**: Recomendacion + lógica FODA / matriz de decisión
  (A/B/C) en `services.py`, portada desde `main.py` original.
- **dashboard**: pantalla principal con KPIs.

## Cómo correr el proyecto

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

Luego entra a `http://127.0.0.1:8000/admin/` para cargar las
Dimensiones/Factores/Subfactores iniciales (puedes basarte en
`guiosad_data.csv` y `factors.csv` del proyecto original), y a
`http://127.0.0.1:8000/` para el sistema.

## Pendiente (marcado con TODO en el código)

- Formularios de `onboarding` (cuestionario de importancia).
- Formularios y templates reales de `evaluations` (Pasos 1 y 2) según
  el diseño de GUIOS Pro+.
- Exportar reporte PDF en `recommendations.views.exportar_reporte`.
- Comando de carga inicial (`manage.py loaddata` o `seed`) desde los
  CSV originales.
