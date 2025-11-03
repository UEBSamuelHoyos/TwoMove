"""
TwoMove URL Configuration
Rutas principales del proyecto TwoMove 🚲
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views



urlpatterns = [

    path('', views.home_view, name='home'),
    # Panel de administración
    path('admin/', admin.site.urls),

    # Rutas del módulo de usuarios (registro, verificación, login, etc.)
    path('usuarios/', include('apps.users.urls')),

    # Rutas futuras: gestión de bicicletas, estaciones y alquileres
    path('bicicletas/', include('apps.bikes.urls')),
    path('estaciones/', include('apps.stations.urls')),
    path('alquileres/', include('apps.rentals.urls')),
    path('pagos/', include('apps.payment.urls')),
    path('transactions/', include('apps.transactions.urls')),
    path('wallet/', include('apps.wallet.urls')),
    path("payment/", include("apps.payment.urls")),
    


]

# ========================
# 📂 Archivos estáticos y multimedia (modo DEBUG)
# ========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
