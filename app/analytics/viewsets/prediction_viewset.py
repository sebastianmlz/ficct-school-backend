from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from django.db.models import Avg

from app.authentication.models import Student
from app.academic.models import Grade, Trimester, Enrollment
from app.analytics.services.prediction_service import performance_prediction_service

@extend_schema(tags=['Analytics - AI Performance Predictions'])
class PerformancePredictionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Train Student Performance Model",
        description="Triggers the training process for the student performance prediction model using historical data."
    )
    @action(detail=False, methods=['post'], url_path='train-model')
    def train_model(self, request):
        result = performance_prediction_service.train_performance_model()
        if result.get("status") == "success":
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Predict Student Performance",
        description="Generates a performance prediction (e.g., average grade for the next trimester) for a specific student."
    )
    @action(detail=True, methods=['get'], url_path='predict', permission_classes=[permissions.IsAuthenticated])
    def predict_performance(self, request, pk=None):
        try:
            student_id = int(pk)
        except ValueError:
            return Response({"error": "Invalid student ID format."}, status=status.HTTP_400_BAD_REQUEST)
            
        prediction = performance_prediction_service.predict_student_performance(student_id=student_id)
        if "error" in prediction:
            return Response(prediction, status=status.HTTP_400_BAD_REQUEST)
        return Response(prediction, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Compare Actual vs. Predicted Performance",
        description="Retrieves actual performance data and predicted performance for a student."
    )
    @action(detail=True, methods=['get'], url_path='compare-performance', permission_classes=[permissions.IsAuthenticated])
    def compare_performance(self, request, pk=None):
        try:
            student_id = int(pk)
            student = get_object_or_404(Student, pk=student_id)
        except ValueError:
            return Response({"error": "Invalid student ID format."}, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        
        prediction_data = performance_prediction_service.predict_student_performance(student_id=student.id)
        
        actual_performance_summary = {"message": "No current/recent trimester grade data found for comparison."}
        
        latest_enrollment = Enrollment.objects.filter(student=student, status='active').order_by('-period__start_date', '-created_at').first()
        if latest_enrollment:
            trimesters_for_enrollment = Trimester.objects.filter(
                period=latest_enrollment.period,
                assessment_items__course=latest_enrollment.course
            ).distinct().order_by('-start_date')

            for trimester_to_check in trimesters_for_enrollment:
                grades_in_trimester = Grade.objects.filter(
                    student=student,
                    assessment_item__trimester=trimester_to_check,
                    assessment_item__course=latest_enrollment.course
                )
                if grades_in_trimester.exists():
                    avg_actual_grade = grades_in_trimester.aggregate(Avg('value'))['value__avg']
                    actual_performance_summary = {
                        "trimester_name": trimester_to_check.name,
                        "period_name": trimester_to_check.period.name,
                        "course_name": latest_enrollment.course.name,
                        "actual_average_grade": round(avg_actual_grade, 2) if avg_actual_grade else None,
                        "number_of_grades_recorded": grades_in_trimester.count()
                    }
                    break

        comparison_data = {
            "student_id": student.id,
            "student_name": student.user.get_full_name(),
            "predicted_performance": prediction_data,
            "actual_performance_summary": actual_performance_summary
        }
        return Response(comparison_data, status=status.HTTP_200_OK)