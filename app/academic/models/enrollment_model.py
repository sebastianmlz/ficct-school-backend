from django.db import models
from core.models.base_model import TimestampedModel

class Enrollment(TimestampedModel):
    ENROLLMENT_STATUS = (
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    )
    
    student = models.ForeignKey('authentication.Student', on_delete=models.CASCADE,
                               related_name='enrollments')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                              related_name='enrollments')
    subject = models.ForeignKey('academic.Subject', on_delete=models.CASCADE,
                               related_name='enrollments')
    period = models.ForeignKey('academic.Period', on_delete=models.CASCADE,
                              related_name='enrollments')
    
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='active')
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course', 'subject', 'period')
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student} - {self.course.name} - {self.subject.name} ({self.period.name})"