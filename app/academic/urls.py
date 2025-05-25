from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.academic.viewsets import (
    CourseViewSet, TeacherAssignmentViewSet,
    PeriodViewSet, SubjectViewSet,
    GradeViewSet, EnrollmentViewSet,
    AttendanceViewSet, ParticipationViewSet,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'teacher-assignments', TeacherAssignmentViewSet, basename='teacher-assignment')
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'participations', ParticipationViewSet, basename='participation')

urlpatterns = [
    path('', include(router.urls)),
]