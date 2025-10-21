from django.urls import path
from . import views

app_name = 'users'  # 👈 esto permite usar rutas como users:login o users:registro

urlpatterns = [
    # 🧾 Registro de nuevo usuario
    path('registro/', views.registro_view, name='registro'),

    # ✅ Verificación de cuenta por código
    path('verificar/', views.verificar_cuenta_view, name='verificar_cuenta'),

    # 🔐 Inicio de sesión
    path('login/', views.login_view, name='login'),

    # 🚪 Cierre de sesión
    path('logout/', views.logout_view, name='logout'),
]
