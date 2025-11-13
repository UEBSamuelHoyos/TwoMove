# apps/users/views.py

from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Sum

from .forms import RegistroForm, VerificacionForm
from .models import Usuario, CambioCredenciales

from django.shortcuts import render
from apps.wallet.models import Wallet
from apps.rentals.models import Rental
from apps.payment.models import MetodoTarjeta
from apps.stations.models import Station

def home_view(request):
    return render(request, 'users/base.html')
def dashboard_view(request):
    user = request.user

    # 🪙 Obtener la billetera del usuario
    wallet, created = Wallet.objects.get_or_create(usuario=user)
    saldo_disponible = wallet.balance if wallet else 0

    # 🚴 Viajes del mes actual
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    viajes_mes = Rental.objects.filter(
        usuario=user, 
        hora_inicio__gte=inicio_mes,
        estado="finalizado"  # Solo contar viajes completados
    ).count()

    # ⏱️ Calcular tiempo total de viajes completados
    # Opción 1: Usando duracion_minutos (RECOMENDADO)
    tiempo_total_minutos = Rental.objects.filter(
        usuario=user,
        estado="finalizado",
        duracion_minutos__isnull=False
    ).aggregate(total=Sum('duracion_minutos'))['total'] or 0
    
    horas = tiempo_total_minutos // 60
    minutos = tiempo_total_minutos % 60
    tiempo_total_str = f"{int(horas)}h {int(minutos)}min"
    
    # Opción 2: Calculando manualmente (ALTERNATIVA si prefieres)
    # rentals = Rental.objects.filter(
    #     usuario=user,
    #     hora_fin__isnull=False,
    #     hora_inicio__isnull=False  # 👈 IMPORTANTE: Validar que ambos existan
    # )
    # tiempo_total = timedelta()
    # for viaje in rentals:
    #     if viaje.hora_fin and viaje.hora_inicio:  # 👈 Doble validación
    #         tiempo_total += (viaje.hora_fin - viaje.hora_inicio)
    # horas, resto = divmod(tiempo_total.total_seconds(), 3600)
    # minutos = int(resto // 60)
    # tiempo_total_str = f"{int(horas)}h {minutos}min"

    # ⭐ Nivel según cantidad de viajes totales (no solo del mes)
    total_viajes = Rental.objects.filter(usuario=user, estado="finalizado").count()
    if total_viajes == 0:
        nivel = "Nuevo"
    elif total_viajes < 5:
        nivel = "Principiante"
    elif total_viajes < 20:
        nivel = "Intermedio"
    elif total_viajes < 50:
        nivel = "Avanzado"
    else:
        nivel = "Experto"

    # 💳 Últimos pagos (si tienes modelo Payment)
    pagos = MetodoTarjeta.objects.filter(usuario=user).order_by('-creado_en')[:5]

    # 📍 Estaciones activas
    estaciones = Station.objects.all()

    contexto = {
        "user": user,
        "wallet": wallet,
        "saldo_disponible": saldo_disponible,
        "viajes_mes": viajes_mes,
        "tiempo_total": tiempo_total_str,
        "nivel": nivel,
        "pagos": pagos,
        "estaciones": estaciones,
    }

    return render(request, "users/dashboard.html", contexto)

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            usuario.generar_codigo_verificacion()

            # Enviar correo con código de verificación
            send_mail(
                subject="Código de verificación - TwoMove 🚲",
                message=f"Hola! Tu código de verificación es: {usuario.codigo_verificacion}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            messages.success(request, "Cuenta creada.")
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
                    return redirect('users:login')
                else:
                    messages.error(request, "Código incorrecto ❌")
            except Usuario.DoesNotExist:
                messages.error(request, "Correo no encontrado ❌")
    else:
        form = VerificacionForm()
    return render(request, 'users/verificar.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        contraseña = request.POST.get('password')

        usuario = authenticate(request, username=email, password=contraseña)

        if usuario is not None:
            if usuario.estado == 'activo':
                login(request, usuario)
                return redirect('users:dashboard')

            else:
                messages.error(request, "Cuenta no verificada o sancionada.")
        else:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, 'users/login.html')



def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('users:login')



def recuperar_contrasena_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            enlace = request.build_absolute_uri(f"/usuarios/restablecer/{uid}/{token}/")

            
            context = {
                'user': user,
                'enlace': enlace,
                'year': timezone.now().year
            }

            html_message = render_to_string('users/email_recuperar_contrasena.html', context)

            
            send_mail(
                subject="Restablecer contraseña - TwoMove 🚲",
                message=f"Hola {user.nombre}, usa este enlace para restablecer tu contraseña: {enlace}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, "Hemos enviado un correo con instrucciones para restablecer tu contraseña.")
        except Usuario.DoesNotExist:
            messages.error(request, "No existe una cuenta con ese correo electrónico.")
    return render(request, 'users/recuperar_contrasena.html')



def restablecer_contrasena_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            nueva = request.POST.get('password1')
            confirmar = request.POST.get('password2')

            if nueva == confirmar:
                user.set_password(nueva)
                user.save()
                CambioCredenciales.objects.create(usuario=user, tipo_cambio='contraseña')
                messages.success(request, "Tu contraseña se ha restablecido correctamente ✅")
                return redirect('users:login')
            else:
                messages.error(request, "Las contraseñas no coinciden.")
        return render(request, 'users/restablecer_contrasena.html', {'valido': True})
    else:
        messages.error(request, "El enlace no es válido o ha expirado.")
        return redirect('users:recuperar_contrasena')


def recordar_usuario_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Usuario.objects.get(email=email)
            mensaje = f"""
Hola {user.nombre},

Tu nombre registrado en TwoMove es: {user.nombre} {user.apellido}
Tu correo de acceso es: {user.email}

Atentamente,  
Equipo TwoMove 🚲
"""
            send_mail(
                subject="Recuperación de nombre de usuario - TwoMove 🚲",
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            CambioCredenciales.objects.create(usuario=user, tipo_cambio='usuario')
            messages.success(request, "Te hemos enviado un correo con tus datos de usuario.")
        except Usuario.DoesNotExist:
            messages.error(request, "No existe una cuenta con ese correo.")
    return render(request, 'users/recordar_usuario.html')
