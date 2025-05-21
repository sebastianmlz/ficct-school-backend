from rest_framework import serializers
from app.academic.models import TeacherAssignment, Course, Subject
from app.authentication.serializers import TeacherListSerializer

class TeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_details = TeacherListSerializer(source='teacher', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    period_name = serializers.CharField(source='period.name', read_only=True)
    
    class Meta:
        model = TeacherAssignment
        fields = [
            'id', 'teacher', 'teacher_details', 'course', 'course_name',
            'subject', 'subject_name', 'period', 'period_name',
            'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']