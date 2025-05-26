from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q, Avg
from app.academic.models import Grade, Period, TeacherAssignment
from app.academic.serializers import GradeSerializer, GradeListSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Grades'])
class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'student_grades']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update'] and hasattr(self.request.user, 'teacher_profile'):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GradeListSerializer
        return GradeSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
            
        active_period = Period.objects.filter(is_active=True).first()
        
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            subject_ids = TeacherAssignment.objects.filter(
                teacher=teacher, 
                period=active_period
            ).values_list('subject_id', flat=True)
            
            return qs.filter(
                period=active_period,
                subject_id__in=subject_ids
            ).distinct()
            
        if hasattr(self.request.user, 'student_profile'):
            return qs.filter(
                student=self.request.user.student_profile,
                period=active_period
            )
            
        return qs.none()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='student', description='Filter by student ID', type=str),
            OpenApiParameter(name='course', description='Filter by course ID', type=str),
            OpenApiParameter(name='subject', description='Filter by subject ID', type=str),
            OpenApiParameter(name='period', description='Filter by period ID', type=str),
            OpenApiParameter(name='min_value', description='Filter by minimum grade value', type=float),
            OpenApiParameter(name='max_value', description='Filter by maximum grade value', type=float),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        course_id = request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        subject_id = request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        period_id = request.query_params.get('period')
        if period_id:
            queryset = queryset.filter(period_id=period_id)
        else:
            active_period = Period.objects.filter(is_active=True).first()
            if active_period:
                queryset = queryset.filter(period=active_period)
        min_value = request.query_params.get('min_value')
        if min_value:
            queryset = queryset.filter(value__gte=float(min_value))
        max_value = request.query_params.get('max_value')
        if max_value:
            queryset = queryset.filter(value__lte=float(max_value))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='student_id', description='Student ID', type=str, required=True),
            OpenApiParameter(name='period_id', description='Period ID (defaults to active period)', type=str),
        ]
    )
    @action(detail=False, methods=['get'])
    def student_grades(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({"detail": "student_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        period_id = request.query_params.get('period_id')
        if period_id:
            period = Period.objects.filter(id=period_id).first()
        else:
            period = Period.objects.filter(is_active=True).first()
        if not period:
            return Response({"detail": "No valid period found."}, status=status.HTTP_404_NOT_FOUND)
        grades = self.get_queryset().filter(student_id=student_id, period=period)
        result = {}
        for grade in grades:
            course_name = grade.course.name
            subject_name = grade.subject.name
            key = f"{course_name} - {subject_name}"
            if key not in result:
                result[key] = []
            result[key].append({
                'id': grade.id,
                'value': grade.value,
                'comments': grade.comments,
                'created_at': grade.created_at
            })
        return Response(result)