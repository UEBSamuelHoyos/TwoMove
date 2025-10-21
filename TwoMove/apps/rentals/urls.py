from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='rentals_index'),
]
