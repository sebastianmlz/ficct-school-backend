from rest_framework import serializers
from django.contrib.auth.models import Group, Permission


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for the Permission model."""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for the Group model."""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        source='permissions',
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_ids']
    
    def create(self, validated_data):
        """Handle group creation with permissions."""
        permissions = validated_data.pop('permissions', [])
        group = Group.objects.create(**validated_data)
        
        for permission in permissions:
            group.permissions.add(permission)
        
        return group
    
    def update(self, instance, validated_data):
        """Update group with permissions."""
        permissions = validated_data.pop('permissions', None)
        
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        if permissions is not None:
            instance.permissions.clear()
            for permission in permissions:
                instance.permissions.add(permission)
        
        return instance