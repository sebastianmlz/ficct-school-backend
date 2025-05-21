from rest_framework import serializers
from app.academic.models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'credit_hours', 'courses', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SubjectListSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'credit_hours', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.count()