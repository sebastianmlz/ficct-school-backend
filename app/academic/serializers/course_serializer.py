from rest_framework import serializers
from app.academic.models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'code', 'description', 'year',
            'capacity', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CourseListSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'year', 'capacity', 'student_count', 'is_active']
    
    def get_student_count(self, obj):
        return obj.enrollments.filter(status='active').count()