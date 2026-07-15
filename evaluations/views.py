from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Factor, Subfactor
from catalog.services import calcular_importancia_sugerida

from .forms import EvaluacionFactorFormSet, EvaluacionSubfactorFormSet, IniciarEvaluacionForm
from .models import Evaluacion, EvaluacionFactor, EvaluacionSubfactor
from .services import (
    actualizar_relevancia,
    calcular_importancia_relativa,
    calcular_ponderacion_subfactores,
    es_relevante,
)


@login_required
@transaction.atomic
def iniciar_evaluacion(request):
    """
    Crea el SoftwareEvaluado + Evaluacion, y "congela" (snapshot) la
    Importancia Sugerida (IS) de cada Factor activo hacia
    EvaluacionFactor.importancia_sugerida_snapshot. IS se calcula con
    catalog.services.calcular_importancia_sugerida (evidencia bibliográfica
    de Scopus combinada con Factor.importancia_base; ver ese módulo para
    el fallback si Scopus no está disponible).
    """
    empresa = request.user.empresa
    if empresa is None:
        # Puede pasar con cuentas superusuario sin empresa asociada: el
        # middleware de cuestionario obligatorio las exime del chequeo,
        # así que sin esta guarda se llega hasta aquí y explota con
        # IntegrityError (empresa_id NOT NULL) al guardar el software.
        messages.error(request, "Tu usuario no está asociado a ninguna empresa.")
        return redirect("dashboard:home")

    if request.method == "POST":
        form = IniciarEvaluacionForm(request.POST)
        if form.is_valid():
            software = form.save(commit=False)
            software.empresa = empresa
            software.save()

            evaluacion = Evaluacion.objects.create(
                empresa=empresa, software=software, creado_por=request.user
            )

            factores_activos = Factor.objects.filter(activo=True).select_related("dimension")

            nuevos = []
            for factor in factores_activos:
                sugerida = calcular_importancia_sugerida(factor)
                # EvaluacionFactor solo maneja interno/externo; los factores
                # "Ambos" del catálogo se tratan como externos para fines
                # de clasificación FODA (simplificación, ajustable a futuro).
                alcance = factor.alcance if factor.alcance in ("interno", "externo") else "externo"

                # Al crear, decisor == sugerida (ver comentario arriba), así
                # que ya podemos calcular relativa/relevante de una vez y
                # que la columna "Import. Relativa" no aparezca vacía la
                # primera vez que se abre el Paso 1.
                relativa_inicial = calcular_importancia_relativa(sugerida, sugerida)

                nuevos.append(EvaluacionFactor(
                    evaluacion=evaluacion,
                    factor=factor,
                    importancia_sugerida_snapshot=sugerida,
                    importancia_decisor=sugerida,
                    importancia_relativa=relativa_inicial,
                    relevante=es_relevante(relativa_inicial),
                    alcance=alcance,
                ))
            EvaluacionFactor.objects.bulk_create(nuevos)

            return redirect("evaluations:paso1", pk=evaluacion.pk)
    else:
        form = IniciarEvaluacionForm()

    return render(request, "evaluations/iniciar.html", {"form": form})


@login_required
def paso1_factores(request, pk):
    """Pantalla 3: Paso 1 - Factores relevantes."""
    evaluacion = get_object_or_404(Evaluacion, pk=pk, empresa=request.user.empresa)
    queryset = evaluacion.factores.select_related("factor", "factor__dimension").order_by(
        "factor__dimension__nombre", "factor__nombre"
    )

    if request.method == "POST":
        formset = EvaluacionFactorFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            # OJO: formset.save(commit=False) omite silenciosamente los
            # forms que el usuario no modificó (Django los considera "sin
            # cambios" si coinciden con el valor inicial). Como
            # pre-cargamos un valor inicial válido, necesitamos procesar
            # TODOS los forms explícitamente, no solo los que cambiaron.
            for subform in formset.forms:
                evaluacion_factor = subform.instance
                evaluacion_factor.importancia_decisor = subform.cleaned_data["importancia_decisor"]
                evaluacion_factor.incluido = subform.cleaned_data["incluido"]
                actualizar_relevancia(evaluacion_factor)  # calcula importancia_relativa + relevante, y guarda

            evaluacion.paso_actual = 2
            evaluacion.save(update_fields=["paso_actual"])

            messages.success(request, "Factores guardados. Continúa con el Paso 2.")
            return redirect("evaluations:paso2", pk=evaluacion.pk)
    else:
        formset = EvaluacionFactorFormSet(queryset=queryset)

    filas = list(zip(queryset, formset.forms))

    return render(request, "evaluations/paso1.html", {
        "evaluacion": evaluacion,
        "formset": formset,
        "filas": filas,
    })


@login_required
def paso2_subfactores(request, pk):
    """
    Pantalla 4: Paso 2 - Evaluación de subfactores.

    Solo entran los factores que salieron RELEVANTES en el Paso 1 y que
    el decisor no excluyó con el toggle "Estado" (incluido=True). Por
    cada uno se garantiza (get_or_create) un EvaluacionSubfactor por
    cada Subfactor activo del catálogo.
    """
    evaluacion = get_object_or_404(Evaluacion, pk=pk, empresa=request.user.empresa)

    # El Paso 1 pre-calcula 'relevante' con valores por defecto desde el
    # momento en que se crea la evaluación (antes de que el decisor
    # revise/confirme nada), así que no basta con chequear que existan
    # factores relevantes: hay que exigir que el Paso 1 ya haya sido
    # enviado (paso_actual >= 2), o se podría saltar directo a este
    # paso por URL sin pasar por el Paso 1.
    if evaluacion.paso_actual < 2:
        messages.warning(request, "Primero debes completar el Paso 1 de esta evaluación.")
        return redirect("evaluations:paso1", pk=evaluacion.pk)

    factores_relevantes = (
        evaluacion.factores
        .filter(relevante=True, incluido=True)
        .select_related("factor")
        .order_by("factor__nombre")
    )

    if not factores_relevantes.exists():
        messages.warning(
            request,
            "No hay factores relevantes para evaluar. Revisa el Paso 1.",
        )
        return redirect("evaluations:paso1", pk=evaluacion.pk)

    # Garantizar que exista un EvaluacionSubfactor por cada Subfactor
    # activo de cada factor relevante (idempotente: get_or_create).
    for evaluacion_factor in factores_relevantes:
        subfactores_activos = Subfactor.objects.filter(factor=evaluacion_factor.factor, activo=True)
        existentes = set(
            evaluacion_factor.subfactores.values_list("subfactor_id", flat=True)
        )
        nuevos = [
            EvaluacionSubfactor(evaluacion_factor=evaluacion_factor, subfactor=sf)
            for sf in subfactores_activos
            if sf.id not in existentes
        ]
        if nuevos:
            EvaluacionSubfactor.objects.bulk_create(nuevos)

    queryset = (
        EvaluacionSubfactor.objects
        .filter(evaluacion_factor__in=factores_relevantes)
        .select_related(
            "subfactor",
            "evaluacion_factor",
            "evaluacion_factor__factor",
            "evaluacion_factor__factor__dimension",
        )
        .order_by(
            "evaluacion_factor__factor__dimension__nombre",
            "evaluacion_factor__factor__nombre",
            "subfactor__id",
        )
    )

    if request.method == "POST":
        formset = EvaluacionSubfactorFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            factores_tocados = set()
            for subform in formset.forms:
                evaluacion_subfactor = subform.instance
                evaluacion_subfactor.valor_cumplimiento = subform.cleaned_data["valor_cumplimiento"]
                evaluacion_subfactor.save()
                factores_tocados.add(evaluacion_subfactor.evaluacion_factor_id)

            for evaluacion_factor in EvaluacionFactor.objects.filter(id__in=factores_tocados):
                calcular_ponderacion_subfactores(evaluacion_factor)

            evaluacion.paso_actual = 3
            evaluacion.save(update_fields=["paso_actual"])

            messages.success(request, "Subfactores guardados. Revisa tu recomendación.")
            return redirect("recommendations:resultado", evaluacion_id=evaluacion.pk)
    else:
        formset = EvaluacionSubfactorFormSet(queryset=queryset)

    # Agrupar (subfactor, subform) por dimensión y factor para que el
    # template pueda pintar la estructura deseada.
    dimensiones = {}
    for evaluacion_subfactor, subform in zip(queryset, formset.forms):
        ef = evaluacion_subfactor.evaluacion_factor
        dimension = ef.factor.dimension
        dimension_data = dimensiones.setdefault(
            dimension,
            {"factores": [], "valores": [], "ponderacion_media": None},
        )

        if not dimension_data["factores"] or dimension_data["factores"][-1]["factor"] != ef:
            dimension_data["factores"].append({"factor": ef, "filas": []})

        dimension_data["factores"][-1]["filas"].append((evaluacion_subfactor, subform))

        if request.method == "POST" and hasattr(subform, "cleaned_data"):
            valor = subform.cleaned_data.get("valor_cumplimiento")
        else:
            valor = evaluacion_subfactor.valor_cumplimiento

        if valor is not None:
            dimension_data["valores"].append(valor)

    for dimension_data in dimensiones.values():
        if dimension_data["valores"]:
            dimension_data["ponderacion_media"] = round(
                sum(dimension_data["valores"]) / len(dimension_data["valores"]), 2
            )

    return render(request, "evaluations/paso2.html", {
        "evaluacion": evaluacion,
        "formset": formset,
        "dimensiones": dimensiones,
    })