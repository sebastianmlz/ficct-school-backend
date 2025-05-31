from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Avg

from app.authentication.models import Student, Teacher
from app.academic.models import Course, Enrollment, Grade, Period

@extend_schema(tags=['Analytics - Dashboards'])
class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser] # Or IsTeacherOrAdmin

    @extend_schema(
        summary="Get General School Statistics",
        description="Provides general statistics for the school dashboard."
    )
    @action(detail=False, methods=['get'], url_path='general-stats')
    def general_stats(self, request):
        active_students_count = Student.objects.filter(user__is_active=True).count()
        active_teachers_count = Teacher.objects.filter(user__is_active=True).count()
        active_courses_count = Course.objects.filter(is_active=True).count()
        
        active_period = Period.objects.filter(is_active=True).first()
        active_enrollments_count = 0
        if active_period:
            active_enrollments_count = Enrollment.objects.filter(period=active_period, status='active').count()

        overall_avg_grade = Grade.objects.aggregate(Avg('value'))['value__avg']

        stats = {
            "active_students_count": active_students_count,
            "active_teachers_count": active_teachers_count,
            "active_courses_count": active_courses_count,
            "active_enrollments_current_period": active_enrollments_count,
            "overall_average_grade": round(overall_avg_grade, 2) if overall_avg_grade else None,
        }
        return Response(stats, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get Course Performance Overview",
        description="Provides an overview of performance per course for the active period."
    )
    @action(detail=False, methods=['get'], url_path='course-performance')
    def course_performance_overview(self, request):
        active_period = Period.objects.filter(is_active=True).first()
        if not active_period:
            return Response({"message": "No active period found."}, status=status.HTTP_404_NOT_FOUND)

        courses_data = []
        courses = Course.objects.filter(is_active=True)
        for course in courses:
            enrollments_in_course = Enrollment.objects.filter(course=course, period=active_period, status='active')
            student_ids_in_course = enrollments_in_course.values_list('student_id', flat=True)
            
            avg_grade_in_course = Grade.objects.filter(
                student_id__in=student_ids_in_course,
                period=active_period 
            ).aggregate(Avg('value'))['value__avg']

            courses_data.append({
                "course_id": course.id,
                "course_name": course.name,
                "enrolled_students": enrollments_in_course.count(),
                "average_grade": round(avg_grade_in_course, 2) if avg_grade_in_course else None
            })
        
        return Response(courses_data, status=status.HTTP_200_OK)