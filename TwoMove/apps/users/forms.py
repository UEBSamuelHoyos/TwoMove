from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password

class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'celular', 'contrasena', 'confirmar_contrasena']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("contrasena") != cleaned_data.get("confirmar_contrasena"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.contrasena_hash = make_password(self.cleaned_data["contrasena"])
        usuario.estado = "inactivo"
        if commit:
            usuario.save()
        return usuario


class VerificacionForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    codigo = forms.CharField(label="Código de verificación", max_length=6)
