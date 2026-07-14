from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Empresa, Usuario


class LoginForm(AuthenticationForm):
    """
    AuthenticationForm de Django reutiliza el campo 'username' por
    debajo, pero en el registro guardamos el correo como username,
    así que aquí solo lo re-etiquetamos para que la pantalla de login
    coincida con el diseño ("Correo Electrónico").
    """
    username = forms.CharField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tu@empresa.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )


class RegistroEmpresaForm(forms.Form):
    """
    Registra una Empresa nueva junto con su primer Usuario
    (rol=administrador). El correo se usa como username internamente.
    """
    empresa_nombre = forms.CharField(label="Nombre de la empresa", max_length=150)
    sector = forms.ChoiceField(label="Sector", choices=Empresa.SECTOR_CHOICES)
    tamano = forms.ChoiceField(label="Tamaño de la empresa", choices=Empresa.TAMANO_CHOICES)

    nombre_usuario = forms.CharField(label="Tu nombre", max_length=150)
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tu@empresa.com"}),
    )
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(username=email).exists():
            raise ValidationError("Ya existe una cuenta registrada con este correo.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        if p1:
            try:
                validate_password(p1)
            except ValidationError as exc:
                self.add_error("password1", exc)

        return cleaned

    def guardar(self):
        """Crea la Empresa y el Usuario administrador asociado, y retorna el Usuario."""
        empresa = Empresa.objects.create(
            nombre=self.cleaned_data["empresa_nombre"],
            sector=self.cleaned_data["sector"],
            tamano=self.cleaned_data["tamano"],
        )
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["nombre_usuario"],
            empresa=empresa,
            rol="administrador",
        )
        return usuario