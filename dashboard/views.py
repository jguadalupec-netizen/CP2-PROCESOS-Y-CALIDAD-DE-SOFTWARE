from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import reverse

from catalog.models import Factor
from evaluations.models import Evaluacion
from recommendations.models import Recomendacion
from recommendations.services import NIVEL_CSS


def _url_para_evaluacion(evaluacion):
    """
    Determina a qué pantalla debe ir el usuario al 'continuar' o 'ver'
    una evaluación, según en qué paso se quedó.
    """
    if evaluacion.paso_actual < 2:
        return reverse("evaluations:paso1", kwargs={"pk": evaluacion.pk})
    if evaluacion.paso_actual < 3:
        return reverse("evaluations:paso2", kwargs={"pk": evaluacion.pk})
    return reverse("recommendations:resultado", kwargs={"evaluacion_id": evaluacion.pk})


def _pasos_stepper(evaluacion):
    """
    Progreso simplificado (Completado/Actual/Pendiente) de los 3 pasos
    de una evaluación, para el stepper visual del dashboard. No hay
    avance parcial dentro de un paso en el esquema actual (Paso 1 y 2
    se envían completos de una sola vez), así que solo se distingue
    entre estos 3 estados por paso.
    """
    definicion = [
        (1, "Factores", evaluacion.paso_actual > 1),
        (2, "Subfactores", evaluacion.paso_actual > 2),
        (3, "Resultado", evaluacion.estado == "completada"),
    ]
    pasos = []
    ya_hay_actual = False
    for numero, etiqueta, completado in definicion:
        if completado:
            estado_paso = "completado"
        elif not ya_hay_actual:
            estado_paso = "actual"
            ya_hay_actual = True
        else:
            estado_paso = "pendiente"
        pasos.append({"numero": numero, "etiqueta": etiqueta, "estado": estado_paso})
    return pasos


@login_required
def home(request):
    """Pantalla 2: Dashboard con KPIs, evaluación en curso y últimas evaluaciones."""
    empresa = request.user.empresa
    evaluaciones_empresa = (
        Evaluacion.objects.filter(empresa=empresa) if empresa else Evaluacion.objects.none()
    )

    factores_registrados = Factor.objects.filter(activo=True).count()
    evaluaciones_completadas = evaluaciones_empresa.filter(estado="completada").count()
    pendientes_evaluacion = evaluaciones_empresa.filter(estado="en_progreso").count()

    # "Evaluación actual": la más reciente que sigue en progreso.
    evaluacion_actual = (
        evaluaciones_empresa.filter(estado="en_progreso")
        .select_related("software")
        .order_by("-fecha_actualizacion")
        .first()
    )

    pasos_evaluacion_actual = None
    continuar_url = None
    if evaluacion_actual:
        continuar_url = _url_para_evaluacion(evaluacion_actual)
        pasos_evaluacion_actual = _pasos_stepper(evaluacion_actual)

    # Últimas evaluaciones (completadas o en progreso): deben poder
    # abrirse todas, cada una en la pantalla que corresponda a su paso.
    ultimas = list(
        evaluaciones_empresa.select_related("software").order_by("-fecha_actualizacion")[:8]
    )
    recomendaciones_por_evaluacion = {
        r.evaluacion_id: r for r in Recomendacion.objects.filter(evaluacion__in=ultimas)
    }

    ultimas_filas = []
    for ev in ultimas:
        recomendacion = recomendaciones_por_evaluacion.get(ev.pk)
        ultimas_filas.append({
            "evaluacion": ev,
            "url": _url_para_evaluacion(ev),
            "recomendacion": recomendacion,
            "nivel_css": NIVEL_CSS.get(recomendacion.nivel, "") if recomendacion else "",
        })

    # Distribución FODA acumulada de todas las evaluaciones completadas
    # de la empresa, para el mini gráfico de dona.
    if empresa:
        totales_foda = Recomendacion.objects.filter(evaluacion__empresa=empresa).aggregate(
            fortalezas=Coalesce(Sum("total_fortalezas"), Value(0)),
            oportunidades=Coalesce(Sum("total_oportunidades"), Value(0)),
            debilidades=Coalesce(Sum("total_debilidades"), Value(0)),
            amenazas=Coalesce(Sum("total_amenazas"), Value(0)),
        )
    else:
        totales_foda = {"fortalezas": 0, "oportunidades": 0, "debilidades": 0, "amenazas": 0}

    total_foda = sum(totales_foda.values())
    donut_gradient_css = None
    if total_foda:
        fin_fortalezas = totales_foda["fortalezas"] / total_foda * 360
        fin_oportunidades = fin_fortalezas + totales_foda["oportunidades"] / total_foda * 360
        fin_debilidades = fin_oportunidades + totales_foda["debilidades"] / total_foda * 360
        # Se arma el string del conic-gradient ya formateado en Python
        # (no interpolando los números directamente en el template):
        # Django localiza los floats en templates (usa coma decimal en
        # es-ES), lo que generaría "95,3deg" e invalidaría la sintaxis CSS.
        donut_gradient_css = (
            "conic-gradient("
            f"#4338ca 0deg {fin_fortalezas:.1f}deg, "
            f"#2e9e5b {fin_fortalezas:.1f}deg {fin_oportunidades:.1f}deg, "
            f"#d64545 {fin_oportunidades:.1f}deg {fin_debilidades:.1f}deg, "
            f"#c2650a {fin_debilidades:.1f}deg 360deg)"
        )

    return render(request, "dashboard/home.html", {
        "factores_registrados": factores_registrados,
        "evaluaciones_completadas": evaluaciones_completadas,
        "pendientes_evaluacion": pendientes_evaluacion,
        "evaluacion_actual": evaluacion_actual,
        "pasos_evaluacion_actual": pasos_evaluacion_actual,
        "continuar_url": continuar_url,
        "ultimas_filas": ultimas_filas,
        "totales_foda": totales_foda,
        "total_foda": total_foda,
        "donut_gradient_css": donut_gradient_css,
    })
