from django.shortcuts import redirect
from django.urls import reverse

# Rutas a las que SIEMPRE se puede acceder aunque el cuestionario
# esté pendiente (para no crear un loop de redirección).
RUTAS_EXENTAS = ("onboarding:cuestionario", "accounts:logout")
PREFIJOS_EXENTOS = ("/admin/", "/static/")


class CuestionarioObligatorioMiddleware:
    """
    Si el usuario pertenece a una Empresa que aún no completó el
    cuestionario inicial de importancia (Empresa.cuestionario_completado
    == False), lo redirige a onboarding:cuestionario sin importar qué
    página haya pedido. Así se garantiza que toda empresa lo responda
    la primera vez que usa el sistema (Pantalla: cuestionario inicial).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._rutas_exentas = None

    def _get_rutas_exentas(self):
        if self._rutas_exentas is None:
            self._rutas_exentas = {reverse(name) for name in RUTAS_EXENTAS}
        return self._rutas_exentas

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user is not None and user.is_authenticated and not user.is_superuser:
            empresa = getattr(user, "empresa", None)
            if empresa is not None and not empresa.cuestionario_completado:
                path = request.path
                if path not in self._get_rutas_exentas() and not path.startswith(PREFIJOS_EXENTOS):
                    return redirect("onboarding:cuestionario")

        return self.get_response(request)