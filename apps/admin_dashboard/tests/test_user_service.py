import pytest
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from apps.admin_dashboard.services.user_service import UsuarioService, UsuarioListResult
from apps.users.models import Usuario
from apps.admin_dashboard.models import Administrador
from apps.rentals.models import Rental
from apps.wallet.models import Wallet


@pytest.mark.django_db
class TestUsuarioService:
    """
    Pruebas unitarias adaptadas al UsuarioService real.
    """

    @pytest.fixture
    def usuario(self, django_user_model):
        return django_user_model.objects.create_user(
            email="user1@test.com",
            password="12345",
            nombre="Fabian",
            apellido="Hoyos",
            celular="3100000000",
            estado="activo",
            is_staff=False
        )

    @pytest.fixture
    def usuario2(self, django_user_model):
        return django_user_model.objects.create_user(
            email="user2@test.com",
            password="12345",
            nombre="Sandra",
            apellido="Amezquita",
            celular="3200000000",
            estado="inactivo",
            is_staff=False
        )

    # ------------------------------------------------------------
    # LISTAR USUARIOS
    # ------------------------------------------------------------
    def test_listar_usuarios_basico(self, usuario, usuario2):
        result = UsuarioService.listar_usuarios(page=1, per_page=10)
        assert isinstance(result, UsuarioListResult)
        assert isinstance(result.page, Paginator.page().__class__)
        assert result.total >= 2
        assert result.query == ""
        assert result.estado is None
        assert result.per_page == 10

    def test_listar_usuarios_con_filtro_y_busqueda(self, usuario, usuario2):
        result = UsuarioService.listar_usuarios(q="Fabian", estado="activo")
        assert result.total == 1
        assert result.estado == "activo"
        assert all(u.estado == "activo" for u in result.page.object_list)

    def test_listar_usuarios_orden_invalido(self, usuario):
        result = UsuarioService.listar_usuarios(ordenar="no_existe")
        assert result.page.number == 1
        assert isinstance(result.page.paginator, Paginator)

    # ------------------------------------------------------------
    # OBTENER USUARIO
    # ------------------------------------------------------------
    def test_obtener_usuario(self, usuario):
        user = UsuarioService.obtener_usuario(usuario.usuario_id)
        assert user.email == usuario.email
        assert isinstance(user, Usuario)

    # ------------------------------------------------------------
    # ACTUALIZAR USUARIO
    # ------------------------------------------------------------
    def test_actualizar_usuario_datos_basicos(self, usuario):
        updated = UsuarioService.actualizar_usuario(
            usuario_id=usuario.usuario_id,
            nombre="Fabian Mod",
            apellido="Hoyos",
            celular="3111111111",
            email="nuevo@test.com",
            estado="activo",
            is_staff=True
        )
        usuario.refresh_from_db()
        assert updated.nombre == "Fabian Mod"
        assert updated.email == "nuevo@test.com"
        assert updated.is_staff is True

    def test_actualizar_usuario_email_duplicado(self, usuario, usuario2):
        with pytest.raises(ValidationError):
            UsuarioService.actualizar_usuario(
                usuario_id=usuario.usuario_id,
                email=usuario2.email
            )

    def test_actualizar_usuario_estado_invalido(self, usuario):
        with pytest.raises(ValidationError):
            UsuarioService.actualizar_usuario(
                usuario_id=usuario.usuario_id,
                estado="pendiente"
            )

    # ------------------------------------------------------------
    # CAMBIAR ACTIVO
    # ------------------------------------------------------------
    def test_cambiar_activo_a_inactivo(self, usuario):
        user = UsuarioService.cambiar_activo(usuario.usuario_id, activo=False)
        assert user.is_active is False
        assert user.estado == "inactivo"

    def test_cambiar_activo_a_activo(self, usuario):
        usuario.estado = "inactivo"
        usuario.save()
        user = UsuarioService.cambiar_activo(usuario.usuario_id, activo=True)
        assert user.is_active is True
        assert user.estado == "activo"

    def test_cambiar_activo_respetando_sancion(self, usuario):
        usuario.estado = "sancionado"
        usuario.save()
        user = UsuarioService.cambiar_activo(usuario.usuario_id, activo=True)
        assert user.estado == "sancionado"

    # ------------------------------------------------------------
    # ELIMINAR USUARIO
    # ------------------------------------------------------------
    def test_eliminar_usuario_basico(self, usuario):
        ok, msg = UsuarioService.eliminar_usuario(usuario.usuario_id)
        assert ok is True
        assert "eliminado" in msg.lower()
        assert not Usuario.objects.filter(usuario_id=usuario.usuario_id).exists()

    def test_eliminar_usuario_administrador_activo(self, usuario):
        Administrador.objects.create(usuario=usuario, activo=True)
        ok, msg = UsuarioService.eliminar_usuario(usuario.usuario_id)
        assert ok is False
        assert "administrador" in msg.lower()

    def test_eliminar_usuario_con_rentals_sin_force(self, usuario):
        Rental.objects.create(usuario=usuario)
        ok, msg = UsuarioService.eliminar_usuario(usuario.usuario_id)
        assert ok is False
        assert "viajes" in msg.lower()

    def test_eliminar_usuario_con_wallet_saldo(self, usuario):
        Wallet.objects.create(usuario=usuario, balance=100)
        ok, msg = UsuarioService.eliminar_usuario(usuario.usuario_id)
        assert ok is False
        assert "saldo" in msg.lower()

    def test_eliminar_usuario_force(self, usuario):
        Rental.objects.create(usuario=usuario)
        Wallet.objects.create(usuario=usuario, balance=500)
        ok, msg = UsuarioService.eliminar_usuario(usuario.usuario_id, force=True)
        assert ok is True
        assert "eliminado" in msg.lower()

    # ------------------------------------------------------------
    # SERIALIZAR USUARIO
    # ------------------------------------------------------------
    def test_serializar_usuario(self, usuario):
        data = UsuarioService.serializar_usuario(usuario)
        assert isinstance(data, dict)
        assert data["usuario_id"] == usuario.usuario_id
        assert "email" in data
        assert "estado" in data
