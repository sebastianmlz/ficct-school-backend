from rest_framework import serializers
from django.contrib.auth.models import Group
from app.authentication.models import Student, User
from app.authentication.serializers.user_serializer import UserSerializer
from drf_spectacular.utils import extend_schema_field
from typing import Union, Optional

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    current_average = serializers.ReadOnlyField()
    attendance_percentage = serializers.ReadOnlyField()
    current_course_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'user', 'student_id', 'enrollment_date',
            'parent_name', 'parent_contact', 'parent_email',
            'emergency_contact', 'medical_info',
            'current_average', 'attendance_percentage',
            'current_course_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    @extend_schema_field(str)
    def get_current_course_name(self, obj) -> Optional[str]:
        course = obj.current_course
        return course.name if course else None
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        groups_data = user_data.pop('groups', [])
        user = User.objects.create_user(**user_data)
        
        if groups_data:
            user.groups.set(groups_data)
        else:
            student_group = Group.objects.get(name='Student')
            user.groups.add(student_group)
            
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            if 'groups' in user_data:
                groups_data = user_data.pop('groups')
                instance.user.groups.set(groups_data)
                
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class StudentListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    full_name = serializers.CharField(source='user.full_name')
    email = serializers.EmailField(source='user.email')
    current_course_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['user_id', 'student_id', 'full_name', 'email', 'current_course_name']
    
    @extend_schema_field(str)
    def get_current_course_name(self, obj) -> Optional[str]:
        course = obj.current_course
        return course.name if course else None