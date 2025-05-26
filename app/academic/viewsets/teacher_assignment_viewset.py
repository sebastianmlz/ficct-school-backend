from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from app.academic.models import TeacherAssignment, Period
from app.academic.serializers import TeacherAssignmentSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Teacher Assignments'])
class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
            
        active_period = Period.objects.filter(is_active=True).first()
        
        if hasattr(self.request.user, 'teacher_profile'):
            return qs.filter(
                teacher=self.request.user.teacher_profile,
                period=active_period
            )
            
        if hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
            course_ids = student.enrollments.filter(
                period=active_period,
                status='active'
            ).values_list('course_id', flat=True)
            
            return qs.filter(
                course_id__in=course_ids,
                period=active_period
            ).distinct()
            
        return qs.none()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='teacher', description='Filter by teacher ID', type=str),
            OpenApiParameter(name='course', description='Filter by course ID', type=str),
            OpenApiParameter(name='subject', description='Filter by subject ID', type=str),
            OpenApiParameter(name='period', description='Filter by period ID', type=str),
        ],
        description="List teacher assignments with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        teacher_id = request.query_params.get('teacher')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        course_id = request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        subject_id = request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        period_id = request.query_params.get('period')
        if period_id:
            queryset = queryset.filter(period_id=period_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)