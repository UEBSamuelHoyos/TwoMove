from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistroForm, VerificacionForm
from .models import Usuario
from django.core.mail import send_mail
from django.conf import settings

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            usuario.generar_codigo_verificacion()
            send_mail(
                subject="Código de verificación - TwoMove 🚲",
                message=f"Tu código es {usuario.codigo_verificacion}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            messages.success(request, "Cuenta creada. Revisa tu correo para verificarla.")
            return redirect('users:verificar_cuenta')

    else:
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})

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
                    return redirect('users:registro')
                else:
                    messages.error(request, "Código incorrecto ❌")
            except Usuario.DoesNotExist:
                messages.error(request, "Correo no encontrado ❌")
    else:
        form = VerificacionForm()
    return render(request, 'users/verificar.html', {'form': form})
