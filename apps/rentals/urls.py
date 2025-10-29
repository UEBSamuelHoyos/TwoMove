# apps/rentals/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rentals', views.RentalViewSet, basename='rental')

app_name = "rentals"

urlpatterns = [
    path('', views.index, name='rentals_index'),

    # ✅ Prueba de reservas (ya existente)
    path('test/reservation/', views.ReservationTestView.as_view(), name='reservation_test'),

    # ✅ NUEVA ruta HTML de prueba de cancelación
    path('test/cancel_reservation/', views.CancelReservationTestView.as_view(), name='cancel_reservation_test'),

    # ✅ Ruta anterior de cancelación por ID (sigue igual)
    path('reservation/<int:rental_id>/cancel/', views.cancel_reservation_view, name='cancel_reservation'),

    # ✅ API principal
    path('api/', include(router.urls)),
]
