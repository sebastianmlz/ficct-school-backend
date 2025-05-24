from rest_framework import serializers
from django.contrib.auth.models import Group
from app.authentication.models import Teacher, User
from app.authentication.serializers.user_serializer import UserSerializer


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Teacher
        fields = [
            'user', 'teacher_id', 'specialization', 'qualification',
            'years_of_experience', 'date_joined', 'employment_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        
        user = User(**user_data)
        if password:
            user.set_password(password)
        user.save()
        
        teacher = Teacher.objects.create(user=user, **validated_data)
        
        teacher_group = Group.objects.get(name='Teacher')
        user.groups.add(teacher_group)
        
        return teacher
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password = user_data.pop('password', None)
        
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        
        if password:
            user.set_password(password)
        
        user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class TeacherListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['user_id', 'user_full_name', 'teacher_id', 'specialization', 'years_of_experience']