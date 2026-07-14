"""
Lógica de recomendación final (Paso 3), portada desde
MainWidget.compute_recommendation() en main.py, y validada contra
MATRIZ_RECOMENDACION_GUIOSAD_2021.xlsx.
"""
from evaluations.models import Evaluacion
from .models import Recomendacion

NIVEL_A = (
    "A",
    "No es posible adoptar. Se han detectado amenazas y/o debilidades en factores cuya "
    "importancia relativa es fundamental o importante, por lo tanto, es indispensable que "
    "el decisor revise los subfactores que no cumplen con lo mínimo requerido para adoptar "
    "la solución. Esta revisión consistiría en proporcionar recursos (humano, tecnológico, "
    "económico, etc.) para mitigar en gran medida los subfactores con baja valoración.",
)
NIVEL_B = (
    "B",
    "Es posible adoptar. A pesar de que se han detectado amenazas y/o debilidades en "
    "factores cuya importancia relativa es opcional, se sugiere revisar los criterios que "
    "no cumplen con lo mínimo requerido para adoptar.",
)
NIVEL_C = (
    "C",
    "Adoptar. Todos los factores han sido identificados como Oportunidades y/o Fortalezas. "
    "Esto quiere decir que la organización cumple satisfactoriamente con la mayoría de "
    "requisitos para adoptar la solución.",
)

FODA_NEGATIVO = {"Amenaza", "Debilidad"}
FODA_POSITIVO = {"Fortaleza", "Oportunidad"}
IMPORTANCIA_ALTA = {"Importante", "Fundamental"}

# Clase CSS por nivel de recomendación (A peor -> C mejor), reutilizada
# tanto en recommendations.views (banner del Paso 3) como en
# dashboard.views (badge en "Últimos softwares evaluados").
NIVEL_CSS = {
    "A": "nivel-negativo",
    "B": "nivel-neutro",
    "C": "nivel-positivo",
}


def generar_recomendacion(evaluacion: Evaluacion) -> Recomendacion:
    # Solo entran al cálculo los factores relevantes que el decisor no
    # haya excluido manualmente de esta evaluación (toggle "Estado").
    factores = evaluacion.factores.filter(relevante=True, incluido=True).exclude(clasificacion_foda="")

    totales = {"Fortaleza": 0, "Oportunidad": 0, "Debilidad": 0, "Amenaza": 0}
    hay_negativo_alta_importancia = False
    hay_negativo_opcional = False
    suma_ponderaciones = 0
    factores_con_ponderacion = 0

    niveles_texto = {1: "Irrelevante", 2: "Opcional", 3: "Importante", 4: "Fundamental"}

    for ef in factores:
        foda = ef.clasificacion_foda
        if foda in totales:
            totales[foda] += 1

        if ef.ponderacion_media is not None:
            suma_ponderaciones += ef.ponderacion_media
            factores_con_ponderacion += 1

        importancia_relativa_txt = niveles_texto.get(ef.importancia_relativa, "")

        if foda in FODA_NEGATIVO and importancia_relativa_txt in IMPORTANCIA_ALTA:
            hay_negativo_alta_importancia = True
        elif foda in FODA_NEGATIVO and importancia_relativa_txt == "Opcional":
            hay_negativo_opcional = True

    puntaje_promedio = (
        round(suma_ponderaciones / factores_con_ponderacion, 2)
        if factores_con_ponderacion
        else None
    )

    if hay_negativo_alta_importancia:
        nivel, texto = NIVEL_A
    elif hay_negativo_opcional:
        nivel, texto = NIVEL_B
    else:
        nivel, texto = NIVEL_C

    recomendacion, _ = Recomendacion.objects.update_or_create(
        evaluacion=evaluacion,
        defaults=dict(
            nivel=nivel,
            texto=texto,
            total_fortalezas=totales["Fortaleza"],
            total_oportunidades=totales["Oportunidad"],
            total_debilidades=totales["Debilidad"],
            total_amenazas=totales["Amenaza"],
            puntaje_promedio=puntaje_promedio,
        ),
    )

    if evaluacion.estado != "completada":
        evaluacion.estado = "completada"
        evaluacion.save(update_fields=["estado"])

    return recomendacion