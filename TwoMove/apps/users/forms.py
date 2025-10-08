from django import forms
from .models import Usuario

class RegistroForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirmar_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'celular']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirmar_password")
        if password and confirmar and password != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = usuario.email  # requerido por AbstractUser
        usuario.set_password(self.cleaned_data["password"])  # guarda con hash
        usuario.estado = "inactivo"
        if commit:
            usuario.save()
        return usuario

class VerificacionForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    codigo = forms.CharField(label="Código de verificación", max_length=6)
