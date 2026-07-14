from django import forms

from .models import EvaluacionFactor, EvaluacionSubfactor, SoftwareEvaluado


class IniciarEvaluacionForm(forms.ModelForm):
    """Datos mínimos para arrancar una nueva Evaluacion (Pantalla 'Nueva evaluación')."""

    class Meta:
        model = SoftwareEvaluado
        fields = ["nombre", "version"]
        labels = {"nombre": "Nombre del software", "version": "Versión"}
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Moodle, OpenProject..."}),
            "version": forms.TextInput(attrs={"placeholder": "Ej. 4.3 (opcional)"}),
        }

    def clean_version(self):
        return self.cleaned_data.get("version", "").strip()


# Un formulario por cada EvaluacionFactor de la evaluación (Paso 1):
# el decisor edita 'importancia_decisor' (sin tocar, como ya estaba) y
# ahora también 'incluido' (el toggle "Estado" del diseño), que permite
# excluir un factor puntual de esta evaluación sin borrarlo.
EvaluacionFactorFormSet = forms.modelformset_factory(
    EvaluacionFactor,
    fields=("importancia_decisor", "incluido"),
    extra=0,
    widgets={
        "importancia_decisor": forms.RadioSelect(choices=EvaluacionFactor.NIVEL_CHOICES),
        "incluido": forms.CheckboxInput(attrs={"class": "toggle-switch-input"}),
    },
)


# Un formulario por cada EvaluacionSubfactor de los factores relevantes
# e incluidos de la evaluación (Paso 2): el decisor califica el
# cumplimiento de cada subfactor (No cumple / Desconozco / Cumple
# parcialmente / Cumple).
EvaluacionSubfactorFormSet = forms.modelformset_factory(
    EvaluacionSubfactor,
    fields=("valor_cumplimiento",),
    extra=0,
    widgets={
        "valor_cumplimiento": forms.RadioSelect(choices=EvaluacionSubfactor.NIVEL_CHOICES),
    },
)