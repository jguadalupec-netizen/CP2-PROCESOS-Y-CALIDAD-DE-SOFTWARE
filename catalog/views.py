from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FactorForm, SubfactorFormSet
from .models import Factor


@login_required
def lista_factores(request):
    """Pantalla 7: Administración de factores."""
    query = request.GET.get("q", "").strip()

    factores = (
        Factor.objects.select_related("dimension")
        .annotate(num_subfactores=Count("subfactores"))
        .order_by("dimension__nombre", "nombre")
    )
    if query:
        factores = factores.filter(
            Q(nombre__icontains=query) | Q(dimension__nombre__icontains=query)
        )

    return render(request, "catalog/administracion.html", {
        "factores": factores,
        "query": query,
    })


@login_required
@transaction.atomic
def crear_factor(request):
    if request.method == "POST":
        form = FactorForm(request.POST)
        if form.is_valid():
            factor = form.save()
            formset = SubfactorFormSet(request.POST, instance=factor)
            if formset.is_valid():
                formset.save()
                messages.success(request, f"Factor «{factor.nombre}» creado correctamente.")
                return redirect("catalog:administracion")
            transaction.set_rollback(True)
        else:
            formset = SubfactorFormSet(request.POST)
    else:
        form = FactorForm()
        formset = SubfactorFormSet()

    return render(request, "catalog/factor_form.html", {
        "form": form,
        "formset": formset,
        "es_nuevo": True,
    })


@login_required
@transaction.atomic
def editar_factor(request, pk):
    factor = get_object_or_404(Factor, pk=pk)

    if request.method == "POST":
        form = FactorForm(request.POST, instance=factor)
        if form.is_valid():
            factor = form.save()
            formset = SubfactorFormSet(request.POST, instance=factor)
            if formset.is_valid():
                formset.save()
                messages.success(request, f"Factor «{factor.nombre}» actualizado correctamente.")
                return redirect("catalog:administracion")
            transaction.set_rollback(True)
        else:
            formset = SubfactorFormSet(request.POST, instance=factor)
    else:
        form = FactorForm(instance=factor)
        formset = SubfactorFormSet(instance=factor)

    return render(request, "catalog/factor_form.html", {
        "form": form,
        "formset": formset,
        "factor": factor,
        "es_nuevo": False,
    })


@login_required
def eliminar_factor(request, pk):
    """
    'Eliminar' un factor lo desactiva (activo=False) en vez de borrarlo
    de la base de datos: factores ya usados en evaluaciones anteriores
    (EvaluacionFactor) dependen de este registro, y un borrado físico
    (on_delete=CASCADE) destruiría esas evaluaciones históricas. Un
    factor inactivo deja de ofrecerse en cuestionarios/evaluaciones
    nuevas, pero conserva el historial.
    """
    factor = get_object_or_404(Factor, pk=pk)
    if request.method == "POST":
        factor.activo = False
        factor.save(update_fields=["activo"])
        messages.success(request, f"Factor «{factor.nombre}» desactivado.")
    return redirect("catalog:administracion")
