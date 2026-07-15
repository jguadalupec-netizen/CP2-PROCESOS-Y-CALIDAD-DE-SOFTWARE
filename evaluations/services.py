"""
Lógica de negocio del Paso 1 y 2 (relevancia y ponderación),
portada desde el guiosad.py / main.py original (flexx).
"""
from .models import EvaluacionFactor


def calcular_importancia_relativa(importancia_sugerida: int, importancia_decisor: int) -> int:
    """
    Combina la importancia sugerida (ahora dinámica, vía onboarding)
    con la evaluación del decisor. Equivale a Guiosad.assigment_function().
    """
    return (importancia_sugerida + importancia_decisor) // 2


def es_relevante(importancia_relativa: int) -> bool:
    """
    Un factor es relevante si su importancia relativa es 'Importante' o
    'Fundamental' (> 2 en la escala 1-4: Irrelevante/Opcional/Importante/
    Fundamental).

    Antes se exigía solo 'Fundamental' (> 3), igual que Guiosad.relevant()
    en guiosad.py. Pero con los valores reales del catálogo (importancia_base
    solo vale 2 o 3 para los 18 factores; ninguno es 4) IS nunca puede pasar
    de 3, así que IR = floor((IS+ID)/2) nunca podía llegar a 4 y ningún
    factor calificaba como relevante nunca. Se bajó el umbral para que el
    Paso 2 sea alcanzable con los datos reales del sistema.
    """
    return importancia_relativa > 2


def actualizar_relevancia(evaluacion_factor: EvaluacionFactor) -> EvaluacionFactor:
    evaluacion_factor.importancia_relativa = calcular_importancia_relativa(
        evaluacion_factor.importancia_sugerida_snapshot,
        evaluacion_factor.importancia_decisor,
    )
    evaluacion_factor.relevante = es_relevante(evaluacion_factor.importancia_relativa)
    evaluacion_factor.save()
    return evaluacion_factor


def calcular_ponderacion_subfactores(evaluacion_factor: EvaluacionFactor) -> EvaluacionFactor:
    """
    Promedia los valores de cumplimiento de los subfactores de un factor
    (Paso 2) y determina su clasificación FODA según el alcance.
    Equivale a MainWidget.btn_sub_pressed() en main.py.
    """
    subfactores = evaluacion_factor.subfactores.all()
    if not subfactores:
        return evaluacion_factor

    promedio = sum(s.valor_cumplimiento for s in subfactores) / len(subfactores)
    evaluacion_factor.ponderacion_media = round(promedio, 2)

    if evaluacion_factor.alcance == "interno":
        evaluacion_factor.clasificacion_foda = "Fortaleza" if promedio >= 3 else "Debilidad"
    else:
        evaluacion_factor.clasificacion_foda = "Oportunidad" if promedio >= 3 else "Amenaza"

    evaluacion_factor.save()
    return evaluacion_factor
