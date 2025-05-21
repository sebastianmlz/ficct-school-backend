from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from app.authentication.serializers import UserSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customized token serializer that includes user data in response"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        user_serializer = UserSerializer(user)
        data['user'] = user_serializer.data
        
        data['roles'] = [group.name for group in user.groups.all()]
        
        data['has_student_profile'] = hasattr(user, 'student_profile')
        data['has_teacher_profile'] = hasattr(user, 'teacher_profile')
        
        if data['has_student_profile']:
            data['student_id'] = user.student_profile.student_id
        
        if data['has_teacher_profile']:
            data['teacher_id'] = user.teacher_profile.teacher_id
        
        return data