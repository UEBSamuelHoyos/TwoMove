from django.urls import path
from .views import crear_transaccion

urlpatterns = [
    path('', crear_transaccion, name='crear_transaccion'),
]
