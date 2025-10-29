from django.apps import AppConfig

class BikesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bikes'   # 👈 IMPORTANTE: incluir el prefijo correcto
    verbose_name = 'Gestión de Bicicletas'
