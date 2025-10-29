from django.apps import AppConfig

class StationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.stations'  # 👈 Debe coincidir con la ruta de la carpeta
    verbose_name = 'Gestión de Estaciones'
