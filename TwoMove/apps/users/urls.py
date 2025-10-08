from django.urls import path
from . import views

app_name = 'users'  # 👈 esto permite usar rutas como users:registro en los templates

urlpatterns = [
   
    path('registro/', views.registro_view, name='registro'),
    path('verificar/', views.verificar_cuenta_view, name='verificar_cuenta'),
   
]
