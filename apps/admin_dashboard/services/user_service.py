# apps/admin_dashboard/services/usuario_service.py
from __future__ import annotations

from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from django.core.paginator import Paginator, Page
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.core.exceptions import ValidationError

from apps.users.models import Usuario
from apps.admin_dashboard.models import Administrador
from apps.rentals.models import Rental
from apps.wallet.models import Wallet


@dataclass
class UsuarioListResult:
    """Contenedor tipado para el resultado del listado paginado."""
    page: Page
    total: int
    query: str
    estado: Optional[str]
    per_page: int


class UsuarioService:
    """
    Servicio de administración de usuarios para el panel avanzado:
      - Listado con filtros, búsqueda y paginación
      - Edición de datos básicos
      - Activar / Inactivar
      - Eliminación segura
    """

    # ------------------------------------------------------------
    # 🔎 LISTADO (búsqueda + filtros + paginación)
    # ------------------------------------------------------------
    @staticmethod
    def listar_usuarios(
        page: int = 1,
        per_page: int = 20,
        q: str = "",
        estado: Optional[str] = None,
        ordenar: str = "-fecha_registro",
    ) -> UsuarioListResult:
        """
        Retorna un Page con usuarios y metadatos de paginación.

        :param page: número de página (1-based)
        :param per_page: tamaño de página
        :param q: texto de búsqueda (email, nombre, apellido, celular)
        :param estado: filtro exacto por estado ('activo', 'inactivo', 'sancionado') o None
        :param ordenar: campo de orden (ej. '-fecha_registro', 'email', '-is_active')
        """
        qs = Usuario.objects.all()

        if q:
            qs = qs.filter(
                Q(email__icontains=q)
                | Q(nombre__icontains=q)
                | Q(apellido__icontains=q)
                | Q(celular__icontains=q)
            )

        if estado:
            qs = qs.filter(estado=estado)

        # Sumar info útil para la tabla (opcional, por si la quieres mostrar)
        # Annotate conteos de viajes y saldo wallet total
        qs = qs.annotate(
            total_viajes=Count("rental", distinct=True),  # si FK en Rental es usuario=ForeignKey(Usuario, related_name='rental')
        )

        # Orden por parámetro (fallback seguro)
        allowed_order = {
            "email", "-email",
            "nombre", "-nombre",
            "apellido", "-apellido",
            "fecha_registro", "-fecha_registro",
            "is_active", "-is_active",
            "estado", "-estado",
        }
        if ordenar not in allowed_order:
            ordenar = "-fecha_registro"

        qs = qs.order_by(ordenar)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        return UsuarioListResult(
            page=page_obj,
            total=paginator.count,
            query=q,
            estado=estado,
            per_page=per_page,
        )

    # ------------------------------------------------------------
    # 🔍 OBTENER UNO
    # ------------------------------------------------------------
    @staticmethod
    def obtener_usuario(usuario_id: int) -> Usuario:
        return Usuario.objects.get(usuario_id=usuario_id)

    # ------------------------------------------------------------
    # ✏️ EDITAR DATOS BÁSICOS
    # ------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def actualizar_usuario(
        usuario_id: int,
        *,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        email: Optional[str] = None,
        celular: Optional[str] = None,
        estado: Optional[str] = None,
        is_staff: Optional[bool] = None,
    ) -> Usuario:
        """
        Actualiza datos básicos del usuario. Valida email único.

        Nota: No cambia password (eso sería otro flujo).
        """
        user = Usuario.objects.select_for_update().get(usuario_id=usuario_id)

        if email and email != user.email:
            if Usuario.objects.filter(email=email).exclude(usuario_id=usuario_id).exists():
                raise ValidationError("Ya existe un usuario con ese correo electrónico.")

        if nombre is not None:
            user.nombre = nombre.strip()
        if apellido is not None:
            user.apellido = apellido.strip()
        if email is not None:
            user.email = email.strip().lower()
        if celular is not None:
            user.celular = celular.strip() if celular else None
        if estado is not None:
            if estado not in {"activo", "inactivo", "sancionado"}:
                raise ValidationError("Estado inválido.")
            user.estado = estado
        if is_staff is not None:
            user.is_staff = bool(is_staff)

        user.save()
        return user

    # ------------------------------------------------------------
    # 📴 ACTIVAR / INACTIVAR
    # ------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def cambiar_activo(usuario_id: int, activo: bool) -> Usuario:
        """
        Cambia el flag is_active del usuario y opcionalmente ajusta 'estado'.
        Regla sugerida:
          - activo=True  -> estado='activo' (si no está sancionado)
          - activo=False -> estado='inactivo'
        """
        user = Usuario.objects.select_for_update().get(usuario_id=usuario_id)
        user.is_active = bool(activo)

        if activo:
            # Si el usuario estaba sancionado, respetamos la sanción (estado no cambia)
            if user.estado != "sancionado":
                user.estado = "activo"
        else:
            user.estado = "inactivo"

        user.save(update_fields=["is_active", "estado"])
        return user

    # ------------------------------------------------------------
    # 🗑️ ELIMINAR (con validaciones)
    # ------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def eliminar_usuario(usuario_id: int, *, force: bool = False) -> Tuple[bool, str]:
        """
        Intenta eliminar un usuario. Por seguridad:
          - No elimina si es Administrador activo.
          - No elimina si tiene rentals, a menos que force=True.
          - Si tiene wallet con balance > 0, no elimina a menos que force=True.

        Retorna (ok, mensaje).
        """
        user = Usuario.objects.select_for_update().get(usuario_id=usuario_id)

        # 1) ¿Es administrador activo?
        if Administrador.objects.filter(usuario=user, activo=True).exists():
            return False, "No se puede eliminar un administrador activo. Descactívelo o quite el rol primero."

        # 2) Rentals
        tiene_rentals = Rental.objects.filter(usuario=user).exists()
        if tiene_rentals and not force:
            return False, "El usuario tiene historial de viajes. Use eliminación forzada o inactívelo."

        # 3) Wallet (si existe modelo y relación uno a uno)
        wallet = Wallet.objects.filter(usuario=user).first()
        if wallet and wallet.balance and wallet.balance > 0 and not force:
            return False, "El usuario tiene saldo en wallet. Debe dejarlo en 0 o usar eliminación forzada."

        # 4) Proceder
        # Si quieres hacer 'soft delete', podrías marcar is_active=False y estado='inactivo'
        # return False, "Eliminación deshabilitada. Se aplicó inactivación (soft delete)."
        user.delete()
        return True, "Usuario eliminado correctamente."

    # ------------------------------------------------------------
    # 🧩 UTILIDADES PARA LA UI AVANZADA
    # ------------------------------------------------------------
    @staticmethod
    def serializar_usuario(user: Usuario) -> Dict[str, Any]:
        """
        Serializa campos útiles para respuestas AJAX de modales.
        """
        return {
            "usuario_id": user.usuario_id,
            "email": user.email,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "celular": user.celular or "",
            "estado": user.estado,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
        }
