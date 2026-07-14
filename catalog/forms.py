from django import forms

from .models import Dimension, Factor, Subfactor


class FactorForm(forms.ModelForm):
    class Meta:
        model = Factor
        fields = ["nombre", "dimension", "importancia_base", "alcance", "descripcion", "activo"]
        labels = {
            "nombre": "Nombre del factor",
            "dimension": "Dimensión",
            "importancia_base": "Importancia sugerida",
            "alcance": "Alcance",
            "descripcion": "Descripción",
            "activo": "Factor activo",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Compatibilidad"}),
            "dimension": forms.Select(),
            "importancia_base": forms.Select(),
            "alcance": forms.Select(),
            "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Descripción opcional del factor..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dimension"].queryset = Dimension.objects.order_by("nombre")
        self.fields["dimension"].empty_label = None


# Un formulario por cada Subfactor del Factor que se está creando/editando.
# can_delete=True habilita el checkbox "Eliminar" en cada fila existente;
# extra=1 agrega siempre una fila vacía al final para capturar subfactores
# nuevos (el resto del "añadir otro" se resuelve con JS en el template).
SubfactorFormSet = forms.inlineformset_factory(
    Factor,
    Subfactor,
    fields=("nombre", "activo"),
    extra=1,
    can_delete=True,
    widgets={
        "nombre": forms.TextInput(attrs={"placeholder": "Nombre del subfactor", "class": "subfactor-nombre"}),
    },
)
