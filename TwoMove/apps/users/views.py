from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail

from .forms import RegistroForm, VerificacionForm
from .models import Usuario

# ==========================
# ✅ Registro de usuario
# ==========================
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            usuario.generar_codigo_verificacion()

            # Enviar correo con código
            send_mail(
                subject="Código de verificación - TwoMove 🚲",
                message=f"Tu código de verificación es: {usuario.codigo_verificacion}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            messages.success(request, "Cuenta creada. Revisa tu correo para verificarla.")
            return redirect('users:verificar_cuenta')
    else:
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})


# ==========================
# ✅ Verificación de cuenta
# ==========================
def verificar_cuenta_view(request):
    if request.method == 'POST':
        form = VerificacionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            codigo = form.cleaned_data['codigo']
            try:
                usuario = Usuario.objects.get(email=email)
                if usuario.codigo_verificacion == codigo:
                    usuario.estado = 'activo'
                    usuario.codigo_verificacion = None
                    usuario.save()
                    messages.success(request, "Cuenta activada correctamente ✅")
                    return redirect('users:login')
                else:
                    messages.error(request, "Código incorrecto ❌")
            except Usuario.DoesNotExist:
                messages.error(request, "Correo no encontrado ❌")
    else:
        form = VerificacionForm()
    return render(request, 'users/verificar.html', {'form': form})


# ==========================
# 🔐 Inicio de sesión
# ==========================
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        contraseña = request.POST.get('password')

        usuario = authenticate(request, username=email, password=contraseña)

        if usuario is not None:
            if usuario.estado == 'activo':
                login(request, usuario)
                return redirect('ruta_post_login')  # 🔁 cambia esto por tu panel o dashboard
            else:
                messages.error(request, "Cuenta no verificada o sancionada.")
        else:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, 'users/login.html')


# ==========================
# 🚪 Cierre de sesión
# ==========================
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('users:login')
