from django.test import SimpleTestCase
from apps.users.apps import UsersConfig


class UsersAppConfigTest(SimpleTestCase):

    def test_nombre_correcto(self):
        """Debe usar el nombre correcto para la app."""
        self.assertEqual(UsersConfig.name, 'apps.users')

    def test_label_correcto(self):
        """Debe usar el label correcto definido como 'users'."""
        self.assertEqual(UsersConfig.label, 'users')
