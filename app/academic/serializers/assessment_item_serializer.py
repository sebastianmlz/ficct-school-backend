from rest_framework import serializers
from app.academic.models import AssessmentItem
from .subject_serializer import SubjectSerializer
from .course_serializer import CourseSerializer
from .trimester_serializer import TrimesterSerializer


class AssessmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentItem
        fields = ['id', 'name', 'assessment_type', 'date', 'max_score', 'subject', 'course', 'trimester', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AssessmentItemDetailSerializer(AssessmentItemSerializer):
    subject = SubjectSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    trimester = TrimesterSerializer(read_only=True)