from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch

from apps.admin_dashboard.services.auth_service import AdminAuthService
from apps.admin_dashboard.models import Administrador


class TestAdminAuthService(TestCase):
    """
    Pruebas unitarias para el servicio de autenticación de administradores (AdminAuthService).
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            email="admin@test.com",
            nombre="Fabian",
            apellido="a",
            password="12345",
        )

        self.request = self.factory.post("/admin/login/")
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.user = AnonymousUser()

    def test_autenticar_admin_exitoso(self):
        admin = Administrador.objects.create(usuario=self.user, activo=True)
        with (
            patch("apps.admin_dashboard.services.auth_service.authenticate", return_value=self.user),
            patch("apps.admin_dashboard.services.auth_service.login") as mock_login,
        ):
            result = AdminAuthService.autenticar_admin(self.request, self.user.email, "secure123")

        self.assertEqual(result, admin)
        mock_login.assert_called_once_with(self.request, self.user)

    def test_autenticar_admin_credenciales_invalidas(self):
        with patch("apps.admin_dashboard.services.auth_service.authenticate", return_value=None):
            with self.assertRaisesMessage(PermissionDenied, "Credenciales inválidas"):
                AdminAuthService.autenticar_admin(self.request, "bad@test.com", "wrongpass")

    def test_autenticar_admin_sin_perfil_admin(self):
        with (
            patch("apps.admin_dashboard.services.auth_service.authenticate", return_value=self.user),
            patch("apps.admin_dashboard.models.Administrador.objects.get", side_effect=Administrador.DoesNotExist),
        ):
            with self.assertRaisesMessage(PermissionDenied, "No tienes permisos para acceder al panel administrativo"):
                AdminAuthService.autenticar_admin(self.request, self.user.email, "secure123")

    def test_autenticar_admin_inactivo(self):
        Administrador.objects.create(usuario=self.user, activo=False)
        with patch("apps.admin_dashboard.services.auth_service.authenticate", return_value=self.user):
            with self.assertRaisesMessage(PermissionDenied, "Tu cuenta de administrador está inactiva"):
                AdminAuthService.autenticar_admin(self.request, self.user.email, "secure123")

    def test_cerrar_sesion(self):
        with patch("apps.admin_dashboard.services.auth_service.logout") as mock_logout:
            AdminAuthService.cerrar_sesion(self.request)
            mock_logout.assert_called_once_with(self.request)
