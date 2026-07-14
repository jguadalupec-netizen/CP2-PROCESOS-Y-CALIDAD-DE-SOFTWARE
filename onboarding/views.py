from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalog.models import Factor
from .forms import CuestionarioImportanciaForm
from .models import HistorialImportancia, PerfilImportanciaFactor


def _procesar_formulario(request, empresa):
    """
    Lógica común a 'primera vez' y 'editar': arma el form con los
    valores actuales, y si es POST válido, guarda PerfilImportanciaFactor
    + registra el cambio en HistorialImportancia (solo si el valor cambió).

    Retorna (form, guardado). Si guardado=True, el caller debe redirigir.
    """
    factores = Factor.objects.filter(activo=True).select_related("dimension")
    valores_actuales = {
        p.factor_id: p.importancia
        for p in PerfilImportanciaFactor.objects.filter(empresa=empresa)
    }

    if request.method == "POST":
        form = CuestionarioImportanciaForm(
            request.POST, factores=factores, valores_iniciales=valores_actuales
        )
        if form.is_valid():
            for factor in factores:
                nuevo_valor = form.cleaned_data[f"factor_{factor.id}"]
                valor_anterior = valores_actuales.get(factor.id)

                if valor_anterior == nuevo_valor:
                    continue  # sin cambios, no tocar ni historial ni updated_at

                PerfilImportanciaFactor.objects.update_or_create(
                    empresa=empresa,
                    factor=factor,
                    defaults={"importancia": nuevo_valor, "actualizado_por": request.user},
                )
                HistorialImportancia.objects.create(
                    empresa=empresa,
                    factor=factor,
                    valor_anterior=valor_anterior,
                    valor_nuevo=nuevo_valor,
                    modificado_por=request.user,
                )

            if not empresa.cuestionario_completado:
                empresa.cuestionario_completado = True
                empresa.save(update_fields=["cuestionario_completado"])

            return form, True
        return form, False

    form = CuestionarioImportanciaForm(factores=factores, valores_iniciales=valores_actuales)
    return form, False


@login_required
def cuestionario_importancia(request):
    """
    Cuestionario inicial. El middleware CuestionarioObligatorioMiddleware
    redirige aquí automáticamente la primera vez que una empresa entra
    al sistema (Empresa.cuestionario_completado == False).
    """
    empresa = request.user.empresa
    if empresa is None:
        messages.error(request, "Tu usuario no está asociado a ninguna empresa.")
        return redirect("dashboard:home")

    form, guardado = _procesar_formulario(request, empresa)
    if guardado:
        messages.success(request, "¡Gracias! Tu perfil de importancia fue guardado.")
        return redirect("dashboard:home")

    return render(request, "onboarding/cuestionario.html", {
        "form": form,
        "empresa": empresa,
        "es_primera_vez": True,
    })


@login_required
def editar_importancia(request):
    """
    Permite a la empresa editar su cuestionario en cualquier momento.
    Reutiliza la misma lógica; cada cambio queda en HistorialImportancia.
    """
    empresa = request.user.empresa
    if empresa is None:
        messages.error(request, "Tu usuario no está asociado a ninguna empresa.")
        return redirect("dashboard:home")

    form, guardado = _procesar_formulario(request, empresa)
    if guardado:
        messages.success(request, "Tu perfil de importancia fue actualizado.")
        return redirect("dashboard:home")

    return render(request, "onboarding/cuestionario.html", {
        "form": form,
        "empresa": empresa,
        "es_primera_vez": False,
    })