from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.academic.viewsets import (
    CourseViewSet, TeacherAssignmentViewSet,
    PeriodViewSet, SubjectViewSet,
    GradeViewSet, EnrollmentViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'teacher-assignments', TeacherAssignmentViewSet, basename='teacher-assignment')
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]