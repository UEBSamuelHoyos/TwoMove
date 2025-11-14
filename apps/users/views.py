# apps/users/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from apps.users.services.registration_service import RegistrationService
from apps.users.services.verification_service import VerificationService
from apps.users.services.auth_service import AuthService
from apps.users.services.password_service import PasswordService
from apps.users.services.user_info_service import UserInfoService

def home_view(request):
    return render(request, 'users/base.html')


def dashboard_view(request):
    contexto = UserInfoService.obtener_dashboard(request.user)
    return render(request, "users/dashboard.html", contexto)


def registro_view(request):
    if request.method == 'POST':
        usuario, error = RegistrationService.registrar_usuario(request)
        if usuario:
            messages.success(request, "Cuenta creada, revisa tu correo.")
            return redirect('users:verificar_cuenta')
        form = error
    else:
        from apps.users.forms import RegistroForm
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})


def verificar_cuenta_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        codigo = request.POST.get("codigo")
        ok, msg = VerificationService.verificar_usuario(email, codigo)

        if ok:
            messages.success(request, "Cuenta verificada.")
            return redirect('users:login')
        else:
            messages.error(request, msg)

    from apps.users.forms import VerificacionForm
    return render(request, 'users/verificar.html', {'form': VerificacionForm()})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        usuario, error = AuthService.iniciar_sesion(request, email, password)

        if usuario:
            return redirect('users:dashboard')
        messages.error(request, error)

    return render(request, 'users/login.html')


def logout_view(request):
    AuthService.cerrar_sesion(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('users:login')


def recuperar_contrasena_view(request):
    if request.method == 'POST':
        ok, msg = PasswordService.enviar_enlace_recuperacion(request, request.POST.get('email'))
        if ok:
            messages.success(request, "Revisa tu correo.")
        else:
            messages.error(request, msg)
    return render(request, 'users/recuperar_contrasena.html')


def restablecer_contrasena_view(request, uidb64, token):
    if request.method == 'POST':
        user, msg = PasswordService.restablecer(
            uidb64, token,
            request.POST.get("password1"),
            request.POST.get("password2")
        )
        if user:
            messages.success(request, "Contraseña cambiada.")
            return redirect('users:login')
        messages.error(request, msg)

    return render(request, 'users/restablecer_contrasena.html', {'valido': True})


def recordar_usuario_view(request):
    if request.method == 'POST':
        ok, msg = UserInfoService.enviar_recordatorio_usuario(request.POST.get("email"))
        if ok:
            messages.success(request, "Correo enviado.")
        else:
            messages.error(request, msg)

    return render(request, 'users/recordar_usuario.html')
