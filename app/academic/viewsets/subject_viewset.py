from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from app.academic.models import Subject, Course, TeacherAssignment, Period, Enrollment
from app.academic.serializers import SubjectSerializer, SubjectListSerializer, CourseListSerializer
from core.pagination import CustomPagination

@extend_schema(tags=['Subjects'])
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'courses']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectListSerializer
        return SubjectSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
            
        active_period = Period.objects.filter(is_active=True).first()
        
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            return qs.filter(
                teacher_assignments__teacher=teacher,
                teacher_assignments__period=active_period
            ).distinct()
            
        if hasattr(self.request.user, 'student_profile'):
            student = self.request.user.student_profile
            course_ids = Enrollment.objects.filter(
                student=student,
                period=active_period,
                status='active'
            ).values_list('course_id', flat=True)
            
            if course_ids:
                return qs.filter(
                    teacher_assignments__course_id__in=course_ids,
                    teacher_assignments__period=active_period
                ).distinct()
                
        return qs.none()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='Search by name or code', type=str),
            OpenApiParameter(name='course', description='Filter by course ID', type=str),
        ],
        description="List subjects with optional filtering"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        course_id = request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(teacher_assignments__course_id=course_id).distinct()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(description="Get courses that teach this subject")
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        subject = self.get_object()
        active_period = Period.objects.filter(is_active=True).first()
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            assignments = TeacherAssignment.objects.filter(subject=subject, period=active_period)
        elif hasattr(self.request.user, 'teacher_profile'):
            assignments = TeacherAssignment.objects.filter(
                subject=subject,
                teacher=self.request.user.teacher_profile,
                period=active_period
            )
        else:
            student = getattr(self.request.user, 'student_profile', None)
            if not student:
                return Response([])
            
            course_ids = Enrollment.objects.filter(
                student=student,
                period=active_period,
                status='active'
            ).values_list('course_id', flat=True)
            
            assignments = TeacherAssignment.objects.filter(
                subject=subject,
                course_id__in=course_ids,
                period=active_period
            )
            
        courses = [assignment.course for assignment in assignments]
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = CourseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)