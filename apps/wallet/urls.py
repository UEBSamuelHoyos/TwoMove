from django.urls import path
from . import views

urlpatterns = [
    path('saldo/', views.obtener_saldo, name='obtener_saldo'),
]
