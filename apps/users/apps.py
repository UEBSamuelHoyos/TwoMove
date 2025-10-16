from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'          # <- esta es la ruta real del módulo
    label = 'users'              # <- este es el app_label que Django usará internamente
