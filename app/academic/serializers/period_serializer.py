from rest_framework import serializers
from app.academic.models import Period

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PeriodListSerializer(serializers.ModelSerializer):
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Period
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active', 'enrollment_count']
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.count()