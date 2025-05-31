from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from app.academic.models import AssessmentItem
from app.academic.serializers import AssessmentItemSerializer, AssessmentItemDetailSerializer
from core.pagination import CustomPagination
from core.permissions import IsTeacherOrAdmin

@extend_schema(tags=['Assessment Items'])
class AssessmentItemViewSet(viewsets.ModelViewSet):
    queryset = AssessmentItem.objects.select_related('subject', 'course', 'trimester__period').all()
    permission_classes = [IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subject', 'course', 'trimester', 'assessment_type', 'trimester__period']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AssessmentItemDetailSerializer
        return AssessmentItemSerializer