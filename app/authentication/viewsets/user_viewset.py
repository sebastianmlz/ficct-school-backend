from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from app.authentication.models import User
from app.authentication.serializers import (
    UserSerializer, UserListSerializer, 
    PasswordChangeSerializer
)
from core.pagination import CustomPagination


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users."""
    
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
        
    @extend_schema(
        description="Partially update a user",
        methods=["PATCH"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Handle partial updates of user data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @extend_schema(
        request=PasswordChangeSerializer,
        responses={200: None},
        description="Change user password with verification"
    )
    @action(
        detail=True,
        methods=['post'],
        serializer_class=PasswordChangeSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def change_password(self, request, pk=None):
        user = self.get_object()
        
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": "Contraseña incorrecta."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        description="Deactivate a user account instead of deleting it"
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser]
    )
    def deactivate(self, request, pk=None):
        """Deactivate a user instead of deleting them."""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response(
            {"detail": "User has been deactivated."},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        description="Reactivate a deactivated user account"
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser]
    )
    def activate(self, request, pk=None):
        """Reactivate a deactivated user."""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response(
            {"detail": "User has been activated."},
            status=status.HTTP_200_OK
        )