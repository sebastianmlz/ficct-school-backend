from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from app.authentication.serializers.auth_serializer import CustomTokenObtainPairSerializer

@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """Customized login view that returns user data along with tokens"""
    serializer_class = CustomTokenObtainPairSerializer