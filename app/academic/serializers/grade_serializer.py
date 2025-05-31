from rest_framework import serializers
from app.academic.models import Grade, AssessmentItem, Enrollment
from app.authentication.serializers import StudentListSerializer
from .subject_serializer import SubjectSerializer
from .period_serializer import PeriodSerializer
from .assessment_item_serializer import AssessmentItemDetailSerializer, AssessmentItemSerializer

class GradeSerializer(serializers.ModelSerializer):
    assessment_item_id = serializers.PrimaryKeyRelatedField(
        queryset=AssessmentItem.objects.all(), source='assessment_item', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'subject', 'period',
            'assessment_item', 'assessment_item_id',
            'value', 'comment', 'date_recorded',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'assessment_item']

    def validate(self, data):
        student = data.get('student')
        assessment_item = data.get('assessment_item')

        if assessment_item:
            data['subject'] = assessment_item.subject
            data['period'] = assessment_item.trimester.period

            if student and assessment_item.course:
                if not Enrollment.objects.filter(
                    student=student,
                    course=assessment_item.course,
                    period=assessment_item.trimester.period,
                    status='active'
                ).exists():
                    raise serializers.ValidationError(
                        f"Student {student} is not actively enrolled in course {assessment_item.course} for period {assessment_item.trimester.period}."
                    )
        elif not data.get('subject') or not data.get('period'):
             raise serializers.ValidationError("If assessment_item is not provided, subject and period are required for a general grade.")

        return data

class GradeDetailSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    period = PeriodSerializer(read_only=True)
    assessment_item = AssessmentItemDetailSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'subject', 'period',
            'assessment_item', 'value', 'comment', 'date_recorded',
            'created_at', 'updated_at'
        ]