from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.db import models
import traceback

from apps.bikes.models import Bike
from apps.rentals.models import Rental
from apps.stations.models import Station
from apps.wallet.models import Wallet
from apps.users.models import Usuario
from apps.admin_dashboard.models import Administrador, Sancion
from .services.auth_service import AdminAuthService
from .services.report_service import ReportService
from .services.sancion_service import SancionService
from django.core.exceptions import ValidationError  
from .services.user_service import UsuarioService 


# ======================================================
# 🔐 LOGIN / LOGOUT
# ======================================================
def admin_login_view(request):
    """Vista de login del administrador"""
    if request.user.is_authenticated:
        try:
            Administrador.objects.get(usuario=request.user, activo=True)
            return redirect("admin_dashboard:dashboard_home")
        except Administrador.DoesNotExist:
            messages.warning(request, "No tienes permisos para el panel administrativo.")
            return redirect("admin_dashboard:admin_logout")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            admin = AdminAuthService.autenticar_admin(request, email, password)
            messages.success(request, f"Bienvenido, {admin.usuario.nombre or admin.usuario.email}")
            return redirect("admin_dashboard:dashboard_home")
        except PermissionDenied as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error en autenticación: {e}")

    return render(request, "admin_dashboard/admin_login.html")


@login_required
def admin_logout_view(request):
    """Cierra la sesión del administrador"""
    AdminAuthService.cerrar_sesion(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("admin_dashboard:admin_login")


# ======================================================
# 📊 DASHBOARD PRINCIPAL
# ======================================================
@login_required
def dashboard_home(request):
    """Página principal del panel administrativo"""
    total_bikes = Bike.objects.count()
    disponibles = Bike.objects.filter(estado="available").count()
    en_uso = Bike.objects.filter(estado="in_use").count()
    mantenimiento = Bike.objects.filter(estado="maintenance").count()

    total_rentals = Rental.objects.count()
    activos = Rental.objects.filter(estado="activo").count()
    finalizados = Rental.objects.filter(estado="finalizado").count()

    total_stations = Station.objects.count()
    total_wallets = Wallet.objects.aggregate(total_balance=models.Sum("balance"))["total_balance"] or 0

    context = {
        "total_bikes": total_bikes,
        "disponibles": disponibles,
        "en_uso": en_uso,
        "mantenimiento": mantenimiento,
        "total_rentals": total_rentals,
        "activos": activos,
        "finalizados": finalizados,
        "total_stations": total_stations,
        "total_wallets": total_wallets,
        "ahora": timezone.now(),
    }
    return render(request, "admin_dashboard/dashboard_home.html", context)


# ======================================================
# 📂 SECCIONES INTERNAS
# ======================================================
@login_required
def usuarios_panel(request):
    return render(request, "admin_dashboard/usuarios_panel.html")


# ======================================================
# 🚫 SANCIÓN DE USUARIOS
# ======================================================
@login_required
def sanciones_panel(request):
    """
    Panel administrativo para gestión de sanciones:
      - Listar sanciones existentes.
      - Crear nuevas sanciones.
      - Levantar sanciones activas.
    """
    try:
        # Verificar permisos
        if not Administrador.objects.filter(usuario=request.user, activo=True).exists():
            raise PermissionDenied("Solo los administradores pueden gestionar sanciones.")

        usuarios = Usuario.objects.all().order_by("email")
        sanciones = Sancion.objects.select_related("usuario").order_by("-fecha_inicio")

        # Crear nueva sanción
        if request.method == "POST":
            usuario_id = request.POST.get("usuario_id")
            motivo = request.POST.get("motivo")
            descripcion = request.POST.get("descripcion", "")
            dias = int(request.POST.get("dias", 3))

            if not usuario_id or not usuario_id.isdigit():
                messages.error(request, "Debe seleccionar un usuario válido.")
                return redirect("admin_dashboard:sanciones_panel")

            usuario = get_object_or_404(Usuario, usuario_id=int(usuario_id))
            SancionService.crear_sancion(usuario, motivo, descripcion, dias, admin=request.user)

            messages.success(request, f"Sanción aplicada correctamente a {usuario.email}.")
            return redirect("admin_dashboard:sanciones_panel")

        context = {
            "usuarios": usuarios,
            "sanciones": sanciones,
        }
        return render(request, "admin_dashboard/sanciones_panel.html", context)

    except PermissionDenied as e:
        print("🚫 Permiso denegado:", e)
        return HttpResponseBadRequest(str(e))

    except Exception as e:
        print("🔥 ERROR al cargar sanciones:", e)
        traceback.print_exc()
        return HttpResponseServerError(f"Ocurrió un error al gestionar las sanciones: {e}")


@login_required
def levantar_sancion(request, sancion_id):
    """
    Desactiva una sanción manualmente desde el panel.
    """
    try:
        if not Administrador.objects.filter(usuario=request.user, activo=True).exists():
            raise PermissionDenied("Solo los administradores pueden levantar sanciones.")

        sancion = get_object_or_404(Sancion, pk=sancion_id)
        SancionService.levantar_sancion(sancion)

        messages.success(request, f"Sanción levantada correctamente para {sancion.usuario.email}.")
        return redirect("admin_dashboard:sanciones_panel")

    except PermissionDenied as e:
        return HttpResponseBadRequest(str(e))
    except Exception as e:
        print("🔥 ERROR al levantar sanción:", e)
        traceback.print_exc()
        return HttpResponseServerError("Error al levantar la sanción.")


# ======================================================
# 📑 REPORTES
# ======================================================
@login_required
def reportes_panel(request):
    """Pantalla para generar reportes"""
    usuarios = Usuario.objects.all().order_by("email")
    return render(request, "admin_dashboard/reportes_panel.html", {"usuarios": usuarios})


@login_required
def descargar_reporte(request):
    """
    Genera y descarga reportes en PDF o CSV.
    Parámetros:
      - tipo: "general" | "usuario"
      - usuario_id: requerido si tipo="usuario"
      - formato: "pdf" | "csv"
    """
    try:
        tipo = (request.GET.get("tipo") or "general").strip().lower()
        formato = (request.GET.get("formato") or "pdf").strip().lower()
        usuario_id = (request.GET.get("usuario_id") or "").strip()

        print("📥 Parámetros recibidos:", request.GET.dict())

        # ----------------------------------------------------------
        # 🔐 Verificación de permisos (solo administradores activos)
        # ----------------------------------------------------------
        if not Administrador.objects.filter(usuario=request.user, activo=True).exists():
            raise PermissionDenied("Solo los administradores pueden generar reportes.")

        # ----------------------------------------------------------
        # 📄 Reporte individual por usuario
        # ----------------------------------------------------------
        if tipo == "usuario":
            if not usuario_id or not usuario_id.isdigit():
                return HttpResponseBadRequest("Debe seleccionar un usuario válido para el reporte individual.")

            usuario = get_object_or_404(Usuario, usuario_id=int(usuario_id))
            data = ReportService.reporte_por_usuario(int(usuario_id))

            # PDF
            if formato == "pdf":
                pdf_buffer = ReportService.generar_pdf_usuario(usuario, data)
                resp = HttpResponse(pdf_buffer, content_type="application/pdf")
                resp["Content-Disposition"] = f'inline; filename="reporte_usuario_{usuario.usuario_id}.pdf"'
                print(f"✅ Reporte PDF individual generado correctamente para {usuario.email}")
                return resp

            # CSV
            if formato == "csv":
                csv_data = ReportService.generar_csv_viajes(data["viajes"])
                resp = HttpResponse(csv_data, content_type="text/csv")
                resp["Content-Disposition"] = f'attachment; filename="reporte_usuario_{usuario.usuario_id}.csv"'
                print(f"✅ Reporte CSV individual generado correctamente para {usuario.email}")
                return resp

            return HttpResponseBadRequest("Formato no soportado para reporte individual.")

        # ----------------------------------------------------------
        # 📊 Reporte general
        # ----------------------------------------------------------
        resumen = ReportService.resumen_general()

        if formato == "pdf":
            pdf_buffer = ReportService.generar_pdf_general(resumen)
            resp = HttpResponse(pdf_buffer, content_type="application/pdf")
            resp["Content-Disposition"] = 'inline; filename="reporte_general.pdf"'
            print("✅ Reporte PDF general generado correctamente.")
            return resp

        if formato == "csv":
            csv_data = (
                "Indicadores,Valor\n"
                f"Total viajes,{resumen['total_viajes']}\n"
                f"Usuarios activos,{resumen['total_usuarios']}\n"
                f"Total recaudado,{resumen['total_recaudado']}\n"
                f"CO2 evitado (kg),{resumen['co2_ev']}\n"
                f"Duración promedio (min),{resumen['promedio_duracion']}\n"
            )
            resp = HttpResponse(csv_data, content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="reporte_general.csv"'
            print("✅ Reporte CSV general generado correctamente.")
            return resp

        return HttpResponseBadRequest("Formato no soportado para reporte general.")

    except PermissionDenied as e:
        print("🚫 Permiso denegado:", e)
        return HttpResponseBadRequest(str(e))

    except Exception as e:
        print("🔥 ERROR al generar reporte:", e)
        traceback.print_exc()
        return HttpResponseServerError(f"Ocurrió un error al generar el reporte: {e}")
    
    # ======================================================
# 👥 GESTIÓN DE USUARIOS (CRUD)
# ======================================================
@login_required
def usuarios_panel(request):
    """Lista y filtra usuarios con búsqueda y paginación"""
    try:
        page = int(request.GET.get("page", 1))
        q = request.GET.get("q", "")
        estado = request.GET.get("estado")
        ordenar = request.GET.get("orden", "-fecha_registro")

        result = UsuarioService.listar_usuarios(page=page, q=q, estado=estado, ordenar=ordenar, per_page=15)

        context = {
            "usuarios": result.page,
            "q": q,
            "estado": estado,
            "total": result.total,
        }
        return render(request, "admin_dashboard/usuarios_panel.html", context)

    except Exception as e:
        print("❌ Error en usuarios_panel:", e)
        traceback.print_exc()
        messages.error(request, "Ocurrió un error al cargar la lista de usuarios.")
        return redirect("admin_dashboard:dashboard_home")


@login_required
def usuarios_editar(request):
    """Actualiza los datos básicos del usuario (modal)"""
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido.")

    try:
        usuario_id = int(request.POST.get("usuario_id"))
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        email = request.POST.get("email")
        celular = request.POST.get("celular")
        estado = request.POST.get("estado")

        UsuarioService.actualizar_usuario(
            usuario_id,
            nombre=nombre,
            apellido=apellido,
            email=email,
            celular=celular,
            estado=estado,
        )

        messages.success(request, "✅ Usuario actualizado correctamente.")
        return redirect("admin_dashboard:usuarios_panel")

    except ValidationError as e:
        messages.error(request, f"Error de validación: {e.messages[0]}")
    except Exception as e:
        print("🔥 Error en usuarios_editar:", e)
        traceback.print_exc()
        messages.error(request, f"Ocurrió un error al actualizar el usuario: {e}")
    return redirect("admin_dashboard:usuarios_panel")


@login_required
def usuarios_toggle(request, usuario_id):
    """Activa o inactiva un usuario"""
    try:
        activo = request.GET.get("activo") == "1"
        user = UsuarioService.cambiar_activo(usuario_id, activo)
        estado_msg = "activado" if activo else "inactivado"
        messages.success(request, f"✅ El usuario {user.email} fue {estado_msg} correctamente.")
    except Exception as e:
        print("🔥 Error al cambiar estado de usuario:", e)
        messages.error(request, f"Ocurrió un error: {e}")
    return redirect("admin_dashboard:usuarios_panel")


@login_required
def usuarios_eliminar(request, usuario_id):
    """Elimina un usuario (con validaciones)"""
    try:
        ok, msg = UsuarioService.eliminar_usuario(usuario_id)
        if ok:
            messages.success(request, msg)
        else:
            messages.warning(request, msg)
    except Exception as e:
        print("🔥 Error al eliminar usuario:", e)
        messages.error(request, f"Ocurrió un error al eliminar el usuario: {e}")
    return redirect("admin_dashboard:usuarios_panel")
