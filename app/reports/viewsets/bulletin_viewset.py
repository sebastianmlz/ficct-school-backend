from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from app.reports.models.bulletin_model import Bulletin
from app.reports.serializers.bulletin_serializer import BulletinSerializer, BulletinGenerationRequestSerializer
from app.reports.services.bulletin_service import bulletin_service
from app.reports.permissions import BulletinPermission

logger = logging.getLogger(__name__)

@extend_schema(tags=['Reports - Bulletins'])
class BulletinViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bulletin.objects.all().select_related(
        'student__user', 
        'trimester__period'
    ).prefetch_related('files').order_by('-generated_at', '-trimester__start_date')
    serializer_class = BulletinSerializer
    permission_classes = [BulletinPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return queryset
            
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
            
        if hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            student_ids = teacher.get_taught_student_ids()
            return queryset.filter(student_id__in=student_ids)
            
        return queryset.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        request=BulletinGenerationRequestSerializer,
        responses={201: BulletinSerializer, 200: BulletinSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
        summary="Generate or re-generate a student's bulletin for a specific trimester",
        description=(
            "Este endpoint genera un boletín para un estudiante específico y un trimestre específico.\n\n"
            "- Admins pueden generar boletines para cualquier estudiante.\n"
            "- Profesores pueden generar boletines solo para estudiantes en sus cursos.\n"
            "- Estudiantes no pueden usar este endpoint.\n\n"
            "**Parámetros:**\n"
            "- `student_id`: ID del estudiante para quien generar el boletín\n"
            "- `trimester_id`: ID del trimestre para el que generar el boletín\n"
            "- `force_regenerate`: Si es true, regenera el boletín aunque ya exista"
        )
    )
    @action(detail=False, methods=['post'], url_path='generate-bulletin')
    def generate_bulletin(self, request):
        if hasattr(request.user, 'student_profile'):
            return Response({"error": "Students cannot generate bulletins"}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = BulletinGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student_id = serializer.validated_data['student_id']
        trimester_id = serializer.validated_data['trimester_id']
        force_regenerate = serializer.validated_data.get('force_regenerate', False)
        
        if hasattr(request.user, 'teacher_profile') and not request.user.is_staff:
            teacher = request.user.teacher_profile
            student_ids = teacher.get_taught_student_ids()
            if int(student_id) not in student_ids:
                return Response(
                    {"error": "You can only generate bulletins for students in your courses"},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            bulletin, generated_this_call = bulletin_service.generate_bulletin_for_student_trimester(
                student_id, 
                trimester_id, 
                force_regenerate,
                generating_user=request.user
            )
            bulletin.refresh_from_db() 
            response_serializer = BulletinSerializer(bulletin, context=self.get_serializer_context())
            response_status = status.HTTP_201_CREATED if generated_this_call else status.HTTP_200_OK
            return Response(response_serializer.data, status=response_status)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Bulletin generation error: {str(e)}", exc_info=True)
            return Response({'error': "An unexpected error occurred during bulletin generation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='student_id', description='Filter bulletins by student ID', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='trimester_id', description='Filter bulletins by trimester ID', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='period_id', description='Filter bulletins by period ID', required=False, type=OpenApiTypes.INT),
        ],
        summary="List bulletins with optional filters",
        description=(
            "Lista los boletines disponibles con filtros opcionales.\n\n"
            "- Admins ven todos los boletines.\n"
            "- Profesores ven boletines de estudiantes en sus cursos.\n"
            "- Estudiantes solo ven sus propios boletines.\n\n"
            "**Filtros opcionales:**\n"
            "- `student_id`: Filtrar por ID de estudiante\n"
            "- `trimester_id`: Filtrar por ID de trimestre\n"
            "- `period_id`: Filtrar por ID de periodo académico"
        )
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        student_id = request.query_params.get('student_id')
        trimester_id = request.query_params.get('trimester_id')
        period_id = request.query_params.get('period_id')

        if student_id:
            if hasattr(request.user, 'student_profile') and int(student_id) != request.user.student_profile.pk:
                return Response(
                    {"error": "Students can only view their own bulletins"},
                    status=status.HTTP_403_FORBIDDEN
                )
            queryset = queryset.filter(student_id=student_id)
            
        if trimester_id:
            queryset = queryset.filter(trimester_id=trimester_id)
            
        if period_id:
            queryset = queryset.filter(trimester__period_id=period_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)