from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from django.db import transaction
import logging
from app.academic.models import Participation, Period, TeacherAssignment
from app.academic.serializers import ParticipationSerializer, ParticipationListSerializer
from core.pagination import CustomPagination

logger = logging.getLogger(__name__)

@extend_schema(tags=['Participations'])
class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.all().order_by('-date')
    serializer_class = ParticipationSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'student_participation']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ParticipationListSerializer
        return ParticipationSerializer
    
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
            OpenApiParameter(name='level', description='Filter by participation level', type=str),
            OpenApiParameter(name='from_date', description='Filter from date (YYYY-MM-DD)', type=str),
            OpenApiParameter(name='to_date', description='Filter to date (YYYY-MM-DD)', type=str),
        ],
        description="List participation records with optional filtering"
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
        level = request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        from_date = request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        to_date = request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
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
        ],
        description="Get participation records for a specific student"
    )
    @action(detail=False, methods=['get'])
    def student_participation(self, request):
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
        records = self.get_queryset().filter(student_id=student_id, period=period)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating participation record: {str(e)}")
            return Response({"detail": f"Error creating participation record: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating participation record: {str(e)}")
            return Response({"detail": f"Error updating participation record: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating participation record: {str(e)}")
            return Response({"detail": f"Error updating participation record: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)