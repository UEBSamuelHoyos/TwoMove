from django.urls import path
from . import views

app_name = 'users'  

urlpatterns = [
  
    path('registro/', views.registro_view, name='registro'),

    path('verificar/', views.verificar_cuenta_view, name='verificar_cuenta'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('recuperar-contrasena/', views.recuperar_contrasena_view, name='recuperar_contrasena'),

    path('restablecer/<uidb64>/<token>/', views.restablecer_contrasena_view, name='restablecer_contrasena'),

    path('recordar-usuario/', views.recordar_usuario_view, name='recordar_usuario'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
  
]
