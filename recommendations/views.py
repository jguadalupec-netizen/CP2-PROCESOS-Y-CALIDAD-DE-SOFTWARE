from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from evaluations.models import Evaluacion
from .services import generar_recomendacion, NIVEL_CSS

# Clasificación FODA -> (clase CSS, icono, título en plural) de la
# insignia/columna correspondiente.
FODA_INFO = {
    "Fortaleza": {"css": "foda-fortaleza", "icono": "↗", "titulo": "Fortalezas"},
    "Oportunidad": {"css": "foda-oportunidad", "icono": "⚡", "titulo": "Oportunidades"},
    "Debilidad": {"css": "foda-debilidad", "icono": "⊘", "titulo": "Debilidades"},
    "Amenaza": {"css": "foda-amenaza", "icono": "⊘", "titulo": "Amenazas"},
}

FODA_ORDEN = ["Fortaleza", "Oportunidad", "Debilidad", "Amenaza"]


@login_required
def resultado(request, evaluacion_id):
    """Pantallas 5/6: Resultado y recomendación (clasificación FODA)."""
    evaluacion = get_object_or_404(Evaluacion, pk=evaluacion_id, empresa=request.user.empresa)

    # El dictamen solo tiene sentido una vez completados los pasos 1 y 2;
    # evita marcar como "completada" (y generar una Recomendación vacía)
    # una evaluación a la que se accedió directamente por URL sin
    # terminar los pasos previos.
    if evaluacion.paso_actual < 3 and evaluacion.estado != "completada":
        messages.warning(request, "Primero debes completar los pasos 1 y 2 de esta evaluación.")
        destino = "evaluations:paso1" if evaluacion.paso_actual < 2 else "evaluations:paso2"
        return redirect(destino, pk=evaluacion.pk)

    recomendacion = generar_recomendacion(evaluacion)

    factores = list(
        evaluacion.factores
        .filter(relevante=True, incluido=True)
        .exclude(clasificacion_foda="")
        .select_related("factor", "factor__dimension")
        .order_by("factor__dimension__nombre", "factor__nombre")
    )

    filas = []
    foda_grupos = {clave: [] for clave in FODA_ORDEN}
    for ef in factores:
        ponderacion = ef.ponderacion_media or 0
        porcentaje = round(float(ponderacion) / 5 * 100, 1)
        info = FODA_INFO.get(ef.clasificacion_foda, {"css": "", "icono": "", "titulo": ef.clasificacion_foda})
        fila = {
            "factor": ef.factor,
            "dimension": ef.factor.dimension.nombre,
            "ponderacion": ponderacion,
            "porcentaje": porcentaje,
            "foda": ef.clasificacion_foda,
            "foda_css": info["css"],
        }
        filas.append(fila)
        if ef.clasificacion_foda in foda_grupos:
            foda_grupos[ef.clasificacion_foda].append({
                "nombre": ef.factor.nombre,
                "ponderacion": ponderacion,
            })

    foda_columnas = [
        {
            "clave": clave,
            "css": FODA_INFO[clave]["css"],
            "icono": FODA_INFO[clave]["icono"],
            "titulo": FODA_INFO[clave]["titulo"],
            "items": foda_grupos[clave],
        }
        for clave in FODA_ORDEN
    ]

    return render(request, "recommendations/resultado.html", {
        "evaluacion": evaluacion,
        "recomendacion": recomendacion,
        "nivel_css": NIVEL_CSS.get(recomendacion.nivel, ""),
        "filas": filas,
        "foda_columnas": foda_columnas,
    })


@login_required
def exportar_reporte(request, evaluacion_id):
    """Exporta el resultado en PDF (botón 'Exportar reporte')."""
    # TODO: usar weasyprint para generar el PDF a partir de resultado.html.
    return resultado(request, evaluacion_id)
