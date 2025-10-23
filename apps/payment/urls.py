from django.urls import path
from . import views

urlpatterns = [
    # Menú principal
    path('', views.menu_pagos, name='menu_pagos'),

    # Flujos de pago individuales
    path('agregar-tarjeta/', views.agregar_tarjeta_view, name='agregar_tarjeta'),
    path('guardar-tarjeta/', views.guardar_tarjeta, name='guardar_tarjeta'),
    
    # HTML view (formulario para usuarios)
    path('recargar-saldo/', views.recargar_saldo_view, name='recargar_saldo'),

    # API REST (solo POST desde frontend móvil)
    path('api/recargar-saldo/', views.recargar_saldo_api, name='recargar_saldo_api'),
    path('eliminar/', views.eliminar_tarjeta_view, name='eliminar_tarjeta_view'),
    path('eliminar/<int:tarjeta_id>/', views.eliminar_tarjeta_id_view, name='eliminar_tarjeta_id_view'),



]
