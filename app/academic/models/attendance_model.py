from django.db import models
from core.models.base_model import TimestampedModel

class Attendance(TimestampedModel):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey('authentication.Student', on_delete=models.CASCADE, 
                               related_name='attendances')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                              related_name='attendances')
    subject = models.ForeignKey('academic.Subject', on_delete=models.CASCADE, 
                               related_name='attendances')
    period = models.ForeignKey('academic.Period', on_delete=models.CASCADE, 
                              related_name='attendances')
    
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='present')
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course', 'subject', 'date', 'period')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.course.name} - {self.subject.name} - {self.date}"