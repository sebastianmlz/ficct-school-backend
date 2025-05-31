from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from app.authentication.serializers.auth_serializer import CustomTokenObtainPairSerializer
from core.models import LoggerService
from django.contrib.auth import get_user_model

User = get_user_model()

@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            email = request.data.get('email', '')
            try:
                user = User.objects.get(email=email)
                
                LoggerService.objects.create(
                    user=user,
                    action='LOGIN',
                    table_name='User',
                    description=f'Usuario {email} ha iniciado sesión exitosamente',
                    level='INFO'
                )
            except User.DoesNotExist:
                pass
            
        return response