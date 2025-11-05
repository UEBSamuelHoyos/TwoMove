from rest_framework import serializers
from .models import BikeTelemetry

class BikeTelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeTelemetry
        fields = [
            "bike_id",
            "latitude",
            "longitude",
            "battery",
            "lock_status",
            "timestamp",
        ]
