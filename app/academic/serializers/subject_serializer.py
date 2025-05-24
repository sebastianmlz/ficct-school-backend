from rest_framework import serializers
from app.academic.models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'credit_hours', 'courses', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_courses(self, obj):
        from app.academic.models import TeacherAssignment
        course_ids = TeacherAssignment.objects.filter(subject=obj).values_list('course_id', flat=True)
        return list(course_ids)

class SubjectListSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'credit_hours', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.count() if hasattr(obj, 'courses') else 0