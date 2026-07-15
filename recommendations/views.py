from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import slugify
from xhtml2pdf import pisa

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
FODA_NEGATIVO = {"Debilidad", "Amenaza"}
IMPORTANCIA_ALTA = {"Importante", "Fundamental"}


def _contexto_resultado(request, evaluacion_id):
    """
    Arma el contexto del Paso 3 (recomendación + clasificación FODA),
    compartido entre la pantalla de resultado y la exportación a PDF.

    Retorna (evaluacion, contexto). Si la evaluación todavía no llegó al
    Paso 3, contexto es None y el caller decide cómo redirigir.
    """
    evaluacion = get_object_or_404(Evaluacion, pk=evaluacion_id, empresa=request.user.empresa)

    # El dictamen solo tiene sentido una vez completados los pasos 1 y 2;
    # evita marcar como "completada" (y generar una Recomendación vacía)
    # una evaluación a la que se accedió directamente por URL sin
    # terminar los pasos previos.
    if evaluacion.paso_actual < 3 and evaluacion.estado != "completada":
        return evaluacion, None

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
        importancia_relativa_txt = ef.get_importancia_relativa_display() if ef.importancia_relativa else ""
        fila = {
            "factor": ef.factor,
            "dimension": ef.factor.dimension.nombre,
            "ponderacion": ponderacion,
            "porcentaje": porcentaje,
            "foda": ef.clasificacion_foda,
            "foda_css": info["css"],
            "importancia_relativa": importancia_relativa_txt,
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

    # Factores que explican por qué el nivel no es A (mejor): el sistema
    # usa una lógica de "veto" donde un solo factor negativo (Debilidad
    # o Amenaza) de importancia alta/opcional puede bajar el nivel aunque
    # el puntaje promedio sea bueno. Se muestran aquí para que quede
    # claro por qué, en vez de que Puntaje y Nivel parezcan contradecirse.
    factores_criticos = []
    if recomendacion.nivel == "C":
        factores_criticos = [
            f for f in filas
            if f["foda"] in FODA_NEGATIVO and f["importancia_relativa"] in IMPORTANCIA_ALTA
        ]
    elif recomendacion.nivel == "B":
        factores_criticos = [
            f for f in filas
            if f["foda"] in FODA_NEGATIVO and f["importancia_relativa"] == "Opcional"
        ]

    contexto = {
        "evaluacion": evaluacion,
        "recomendacion": recomendacion,
        "nivel_css": NIVEL_CSS.get(recomendacion.nivel, ""),
        "filas": filas,
        "foda_columnas": foda_columnas,
        "factores_criticos": factores_criticos,
    }
    return evaluacion, contexto


def _redirigir_paso_incompleto(request, evaluacion):
    messages.warning(request, "Primero debes completar los pasos 1 y 2 de esta evaluación.")
    destino = "evaluations:paso1" if evaluacion.paso_actual < 2 else "evaluations:paso2"
    return redirect(destino, pk=evaluacion.pk)


@login_required
def resultado(request, evaluacion_id):
    """Pantallas 5/6: Resultado y recomendación (clasificación FODA)."""
    evaluacion, contexto = _contexto_resultado(request, evaluacion_id)
    if contexto is None:
        return _redirigir_paso_incompleto(request, evaluacion)

    return render(request, "recommendations/resultado.html", contexto)


@login_required
def exportar_reporte(request, evaluacion_id):
    """Exporta el resultado del Paso 3 en PDF (botón 'Exportar reporte')."""
    evaluacion, contexto = _contexto_resultado(request, evaluacion_id)
    if contexto is None:
        return _redirigir_paso_incompleto(request, evaluacion)

    contexto["generado_en"] = timezone.now()
    html = render_to_string("recommendations/resultado_pdf.html", contexto, request=request)

    buffer = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)
    if pdf.err:
        messages.error(request, "No se pudo generar el PDF del reporte. Intenta de nuevo.")
        return redirect("recommendations:resultado", evaluacion_id=evaluacion.pk)

    nombre_archivo = f"reporte-{slugify(str(evaluacion.software))}-{evaluacion.pk}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    return response
