from django.db import models
from core.models.base_model import TimestampedModel

class Subject(TimestampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)
    credit_hours = models.PositiveIntegerField(default=3)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_courses_in_period(self, period_id):
        from app.academic.models import TeacherAssignment
        assignments = TeacherAssignment.objects.filter(subject=self, period_id=period_id)
        return [assignment.course for assignment in assignments]