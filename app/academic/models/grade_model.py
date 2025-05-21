from django.db import models
from core.models.base_model import TimestampedModel

class Grade(TimestampedModel):
    student = models.ForeignKey('authentication.Student', on_delete=models.CASCADE, 
                               related_name='grades')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                              related_name='grades')
    subject = models.ForeignKey('academic.Subject', on_delete=models.CASCADE, 
                               related_name='grades')
    period = models.ForeignKey('academic.Period', on_delete=models.CASCADE, 
                              related_name='grades')
    
    value = models.FloatField()
    comments = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course', 'subject', 'period')
        ordering = ['-period__start_date', 'student__user__first_name']
    
    def __str__(self):
        return f"{self.student} - {self.course.name} - {self.subject.name}: {self.value}"