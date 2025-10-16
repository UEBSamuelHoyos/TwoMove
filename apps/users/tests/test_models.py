from django.test import TestCase
from django.utils import timezone
from apps.users.models import Usuario, CambioCredenciales

# =====================================
# 🔹 PRUEBAS PARA EL MODELO USUARIO
# =====================================

class UsuarioModelTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="test@correo.com",
            nombre="Samuel",
            apellido="Hoyos",
            password="clave123"
        )

    def test_creacion_usuario_valido(self):
        """Verifica que el usuario se cree correctamente."""
        self.assertEqual(self.user.email, "test@correo.com")
        self.assertTrue(self.user.check_password("clave123"))
        self.assertEqual(self.user.estado, "inactivo")  # por defecto
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_creacion_usuario_sin_email(self):
        """Debe lanzar un error si el email no se proporciona."""
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(
                email="",
                nombre="Laura",
                apellido="Ramírez",
                password="clave123"
            )

    def test_creacion_superusuario(self):
        """Verifica la creación de superusuario con flags correctos."""
        superuser = Usuario.objects.create_superuser(
            email="admin@correo.com",
            nombre="Admin",
            apellido="Root",
            password="admin123"
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.estado, "activo")

    def test_codigo_verificacion_generado(self):
        """Debe generar un código de 6 dígitos y guardarlo."""
        self.user.generar_codigo_verificacion()
        self.assertIsNotNone(self.user.codigo_verificacion)
        self.assertEqual(len(self.user.codigo_verificacion), 6)
        self.assertTrue(self.user.codigo_verificacion.isdigit())

    def test_str_representacion(self):
        """Debe mostrar nombre, apellido y correo."""
        representacion = str(self.user)
        self.assertIn("Samuel", representacion)
        self.assertIn("Hoyos", representacion)
        self.assertIn("test@correo.com", representacion)


# =====================================
# 🔹 PRUEBAS PARA CAMBIO DE CREDENCIALES
# =====================================

class CambioCredencialesModelTest(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="usuario@correo.com",
            nombre="Carlos",
            apellido="Pérez",
            password="clave123"
        )

    def test_creacion_registro_cambio(self):
        """Debe crear un registro de cambio de credenciales correctamente."""
        cambio = CambioCredenciales.objects.create(
            usuario=self.user,
            tipo_cambio="contraseña"
        )
        self.assertEqual(cambio.usuario, self.user)
        self.assertEqual(cambio.tipo_cambio, "contraseña")
        self.assertIsNotNone(cambio.fecha)

    def test_str_representacion(self):
        """Debe mostrar email, tipo y fecha en string."""
        cambio = CambioCredenciales.objects.create(
            usuario=self.user,
            tipo_cambio="usuario"
        )
        representacion = str(cambio)
        self.assertIn("usuario@correo.com", representacion)
        self.assertIn("usuario", representacion)
        self.assertIn(str(cambio.fecha.year), representacion)
