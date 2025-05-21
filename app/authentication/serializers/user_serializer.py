from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from app.authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model with password handling."""
    
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False
    )
    
    group_names = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'address', 'date_of_birth', 'password',
            'is_active', 'groups', 'group_names', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']
    
    def get_group_names(self, obj):
        """Get the names of groups this user belongs to."""
        return [group.name for group in obj.groups.all()]
    
    def create(self, validated_data):
        """Handle user creation with password hashing."""
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        
        if password:
            user.set_password(password)
        
        user.save()
        
        for group in groups:
            user.groups.add(group)
            
        return user
    
    def update(self, instance, validated_data):
        """Update user but handle password separately for hashing."""
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        if groups is not None:
            instance.groups.clear()
            for group in groups:
                instance.groups.add(group)
                
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing users."""
    
    group_names = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'group_names', 'created_at']
    
    def get_group_names(self, obj):
        """Get the names of groups this user belongs to."""
        return [group.name for group in obj.groups.all()]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Ensure the new password and confirm password match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields don't match."})
        return attrs