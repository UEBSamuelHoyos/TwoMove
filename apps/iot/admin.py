from django.contrib import admin
from .models import BikeTelemetry

@admin.register(BikeTelemetry)
class BikeTelemetryAdmin(admin.ModelAdmin):
    list_display = ("bike_id", "latitude", "longitude", "battery", "lock_status", "timestamp")
    list_filter = ("lock_status", "bike_id")
    search_fields = ("bike_id",)
    ordering = ("-timestamp",)
