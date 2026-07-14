from django.contrib.auth import login as auth_login
from django.shortcuts import redirect, render

from .forms import RegistroEmpresaForm


def registro_empresa(request):
    """
    Registro de una nueva Empresa + su primer Usuario (administrador).
    Al terminar, deja al usuario logueado y lo manda al dashboard; el
    middleware de onboarding se encarga de redirigirlo al cuestionario
    inicial automáticamente (empresa.cuestionario_completado == False).
    """
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegistroEmpresaForm(request.POST)
        if form.is_valid():
            usuario = form.guardar()
            auth_login(request, usuario)
            return redirect("dashboard:home")
    else:
        form = RegistroEmpresaForm()

    return render(request, "accounts/registro.html", {"form": form})