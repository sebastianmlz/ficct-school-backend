from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from app.authentication.serializers import GroupSerializer, PermissionSerializer
from app.authentication.models import User
from core.pagination import CustomPagination


@extend_schema(tags=['Roles & Permissions'])
class GroupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing groups (roles)."""
    
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    pagination_class = CustomPagination

    @extend_schema(
    description="Partially update a group/role",
    methods=["PATCH"]
)
    def partial_update(self, request, *args, **kwargs):
        """Handle partial updates of group data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @extend_schema(
        description="Get users assigned to this group"
    )
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Return list of users that belong to this group."""
        group = self.get_object()
        users = User.objects.filter(groups=group)
        
        from app.authentication.serializers import UserListSerializer
        serializer = UserListSerializer(users, many=True)
        
        return Response(serializer.data)
    
    @extend_schema(
        description="Add a user to this group"
    )
    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        """Add a user to this group."""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user.groups.filter(id=group.id).exists():
            return Response(
                {"detail": "User is already in this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.groups.add(group)
        
        return Response(
            {"detail": f"User {user.email} added to group {group.name}."},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        description="Remove a user from this group"
    )
    @action(detail=True, methods=['post'])
    def remove_user(self, request, pk=None):
        """Remove a user from this group."""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not user.groups.filter(id=group.id).exists():
            return Response(
                {"detail": "User is not in this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.groups.remove(group)
        
        return Response(
            {"detail": f"User {user.email} removed from group {group.name}."},
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['Roles & Permissions'])
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing permissions (read-only)."""
    
    queryset = Permission.objects.all().order_by('codename')
    serializer_class = PermissionSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
    description="Partially update a group/role",
    methods=["PATCH"]
)
    def partial_update(self, request, *args, **kwargs):
        """Handle partial updates of group data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @extend_schema(
        description="List available permissions, optionally filtered by app"
    )
    def list(self, request, *args, **kwargs):
        """List permissions with optional app filtering."""
        queryset = self.get_queryset()
        
        app_label = request.query_params.get('app', None)
        if app_label:
            queryset = queryset.filter(content_type__app_label=app_label)
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(codename__icontains=search)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)