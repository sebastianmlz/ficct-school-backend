from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from app.academic.models import Subject, Course
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
        if hasattr(self.request.user, 'teacher'):
            ids = qs.filter(teacherassignments__teacher=self.request.user.teacher).values_list('id', flat=True)
            return qs.filter(id__in=ids).distinct()
        if hasattr(self.request.user, 'student'):
            from app.academic.models import Enrollment
            course_ids = Enrollment.objects.filter(student=self.request.user.student).values_list('course_id', flat=True)
            return qs.filter(teacherassignments__course_id__in=course_ids).distinct()
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
            queryset = queryset.filter(courses__id=course_id)
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
        courses = subject.courses.all()
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = CourseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)