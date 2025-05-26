from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from django.db import transaction
import logging
from app.academic.models import Attendance, Period, TeacherAssignment
from app.academic.serializers import AttendanceSerializer, AttendanceListSerializer
from core.pagination import CustomPagination

logger = logging.getLogger(__name__)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-date')
    serializer_class = AttendanceSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'student_attendance']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return AttendanceListSerializer
        return AttendanceSerializer
    
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
            OpenApiParameter(name='student_id', description='Student ID', type=str, required=True),
            OpenApiParameter(name='period_id', description='Period ID (defaults to active period)', type=str),
        ]
    )
    @action(detail=False, methods=['get'])
    def student_attendance(self, request):
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
            logger.error(f"Error creating attendance record: {str(e)}")
            return Response({"detail": f"Error creating attendance record: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating attendance record: {str(e)}")
            return Response({"detail": f"Error updating attendance record: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating attendance record: {str(e)}")
            return Response({"detail": f"Error updating attendance record: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)