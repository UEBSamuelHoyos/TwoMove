# apps/rentals/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 🔧 Router para el ViewSet principal
router = DefaultRouter()
router.register(r'rentals', views.RentalViewSet, basename='rental')

app_name = "rentals"

urlpatterns = [
    # ---------------------------------------------------
    # 🌐 Página principal del módulo
    # ---------------------------------------------------
    path('', views.index, name='rentals_index'),

    # ---------------------------------------------------
    # 🧩 Páginas HTML de prueba
    # ---------------------------------------------------
    path('test/reservation/', views.ReservationTestView.as_view(), name='reservation_test'),
    path('test/cancel_reservation/', views.CancelReservationTestView.as_view(), name='cancel_reservation_test'),
    path('reservation/<int:rental_id>/cancel/', views.cancel_reservation_view, name='cancel_reservation'),
    path('test/start_trip/', views.StartTripTestView.as_view(), name='start_trip_test'),
    path('test/trip-end/', views.TripEndPageView.as_view(), name='trip_end_page'),
    path('test/trip-history/', views.trip_history_view, name='trip_history'),    

    # ---------------------------------------------------
    # ⚙️ Endpoint API HTML (TripEnd desde formulario)
    # ---------------------------------------------------
    path('api/trip-end/', views.TripEndAPI.as_view(), name='trip_end_api'),

    # ---------------------------------------------------
    # 🚀 API REST principal (ViewSet)
    # ---------------------------------------------------
    path('api/', include(router.urls)),
]
