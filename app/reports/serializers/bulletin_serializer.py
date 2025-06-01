from rest_framework import serializers
from app.reports.models.bulletin_model import Bulletin, BulletinFile
from app.authentication.serializers.student_serializer import StudentListSerializer
from app.academic.serializers.trimester_serializer import TrimesterSerializer

class BulletinFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = BulletinFile
        fields = ['id', 'format', 'file', 'url', 'created_at']
        read_only_fields = ['id', 'file', 'url', 'created_at']
    
    def get_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

class BulletinSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True)
    trimester = TrimesterSerializer(read_only=True)
    files = BulletinFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Bulletin
        fields = [
            'id', 'student', 'trimester', 'overall_average', 'grades_data', 
            'status', 'files', 'generated_at', 'created_at', 'updated_at', 
            'error_message'
        ]
        read_only_fields = [
            'id', 'student', 'trimester', 'overall_average', 'grades_data', 
            'status', 'files', 'generated_at', 'created_at', 'updated_at', 
            'error_message'
        ]

class BulletinGenerationRequestSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(required=True)
    trimester_id = serializers.IntegerField(required=True)
    force_regenerate = serializers.BooleanField(default=False)