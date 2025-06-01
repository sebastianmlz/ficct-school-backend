from django.db import models
from .user_model import User
from core.models.base_model import TimestampedModel

class Teacher(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', primary_key=True)
    teacher_id = models.CharField(max_length=20, unique=True)
    
    specialization = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    date_joined = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=50, default='active', 
                                         choices=(('active', 'Active'), 
                                                  ('inactive', 'Inactive'),
                                                  ('on_leave', 'On Leave')))
    
    def __str__(self):
        return f"Teacher: {self.user.full_name} ({self.teacher_id})"
    
    @property
    def assigned_courses(self):
        from app.academic.models import Period
        active_period = Period.objects.filter(is_active=True).first()
        if not active_period:
            return []
        return [assignment.course for assignment in self.assignments.filter(period=active_period)]
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def get_taught_student_ids(self):
        from app.academic.models import TeacherAssignment, Enrollment
        
        teacher_assignments = TeacherAssignment.objects.filter(
            teacher=self
        ).values_list('course_id', 'period_id')
        
        student_ids = []
        
        if teacher_assignments:
            course_ids = [ta[0] for ta in teacher_assignments]
            period_ids = [ta[1] for ta in teacher_assignments]
            
            enrollments = Enrollment.objects.filter(
                course_id__in=course_ids,
                period_id__in=period_ids,
                status='active'
            ).values_list('student_id', flat=True).distinct()
            
            student_ids = list(enrollments)
        
        return student_ids