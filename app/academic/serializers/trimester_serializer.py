from rest_framework import serializers
from app.academic.models import Trimester

class TrimesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trimester
        fields = ['id', 'name', 'period', 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']