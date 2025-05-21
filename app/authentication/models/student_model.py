from django.db import models
from .user_model import User
from core.models.base_model import TimestampedModel

class Student(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', primary_key=True)
    student_id = models.CharField(max_length=20, unique=True)
    
    enrollment_date = models.DateField(null=True, blank=True)
    
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_contact = models.CharField(max_length=20, null=True, blank=True)
    parent_email = models.EmailField(null=True, blank=True)
    
    emergency_contact = models.CharField(max_length=20, null=True, blank=True)
    medical_info = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Student: {self.user.full_name} ({self.student_id})"
    
    @property
    def current_course(self):
        from app.academic.models import Period, Enrollment
        active_period = Period.objects.filter(is_active=True).first()
        if not active_period:
            return None
        active_enrollment = self.enrollments.filter(period=active_period, status='active').first()
        return active_enrollment.course if active_enrollment else None
    
    @property
    def current_average(self):
        from app.academic.models import Period
        active_period = Period.objects.filter(is_active=True).first()
        if not active_period:
            return 0
        
        grades = self.grades.filter(period=active_period)
        
        if not grades.exists():
            return 0
            
        total = sum(grade.value for grade in grades)
        return total / grades.count()
    
    @property
    def attendance_percentage(self):
        from app.academic.models import Period
        active_period = Period.objects.filter(is_active=True).first()
        if not active_period:
            return 100
        
        attendances = self.attendances.filter(period=active_period)
        
        if not attendances.exists():
            return 100
            
        present_count = attendances.filter(status='present').count()
        return (present_count / attendances.count()) * 100
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']