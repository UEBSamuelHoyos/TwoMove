# apps/users/forms.py
from django import forms
from .models import Usuario

class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'celular', 'contrasena', 'confirmar_contrasena']

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")

        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["contrasena"])  # 🔑 Hashea correctamente
        if commit:
            user.save()
        return user


class VerificacionForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    codigo = forms.CharField(label="Código de verificación", max_length=6)
