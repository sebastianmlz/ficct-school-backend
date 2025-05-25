from django.db import models
from core.models.base_model import TimestampedModel

class Participation(TimestampedModel):
    PARTICIPATION_LEVELS = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('none', 'None'),
    )
    
    student = models.ForeignKey('authentication.Student', on_delete=models.CASCADE, 
                               related_name='participations')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                              related_name='participations')
    subject = models.ForeignKey('academic.Subject', on_delete=models.CASCADE, 
                               related_name='participations')
    period = models.ForeignKey('academic.Period', on_delete=models.CASCADE, 
                              related_name='participations')
    
    date = models.DateField()
    level = models.CharField(max_length=20, choices=PARTICIPATION_LEVELS, default='medium')
    comments = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course', 'subject', 'date', 'period')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.course.name} - {self.subject.name} - {self.date}"