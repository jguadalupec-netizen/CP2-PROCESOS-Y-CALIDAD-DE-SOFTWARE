from django import forms
from catalog.models import Factor

NIVEL_CHOICES = [
    (1, "Irrelevante"),
    (2, "Opcional"),
    (3, "Importante"),
    (4, "Fundamental"),
]


class CuestionarioImportanciaForm(forms.Form):
    """
    Formulario dinámico: genera un campo de importancia (1-4) por cada
    Factor activo del catálogo. Es dinámico porque el catálogo es
    editable desde el panel de Administración (catalog app), así que
    no se puede fijar la lista de campos de antemano.
    """

    def __init__(self, *args, factores=None, valores_iniciales=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.factores = list(
            factores
            if factores is not None
            else Factor.objects.filter(activo=True).select_related("dimension")
        )
        valores_iniciales = valores_iniciales or {}

        for factor in self.factores:
            field_name = f"factor_{factor.id}"
            self.fields[field_name] = forms.TypedChoiceField(
                label=factor.nombre,
                choices=NIVEL_CHOICES,
                coerce=int,
                widget=forms.RadioSelect,
                initial=valores_iniciales.get(factor.id, factor.importancia_base),
            )

    def factores_con_campos(self):
        """
        Agrupa (factor, campo_del_formulario) por Dimensión, para
        que el template los pinte organizados por sección.
        """
        agrupado = {}
        for factor in self.factores:
            bound_field = self[f"factor_{factor.id}"]
            agrupado.setdefault(factor.dimension, []).append((factor, bound_field))
        return agrupado