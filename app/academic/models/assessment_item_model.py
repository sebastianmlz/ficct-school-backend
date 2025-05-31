from django.db import models
from core.models import TimestampedModel
from .subject_model import Subject
from .course_model import Course
from .trimester_model import Trimester

class AssessmentItem(TimestampedModel):
    ASSESSMENT_TYPES = [
        ('EXAM', 'Exam'),
        ('TASK', 'Task'),
        ('PROJECT', 'Project'),
        ('PARTICIPATION', 'Participation'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='EXAM')
    date = models.DateField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessment_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessment_items')
    trimester = models.ForeignKey(Trimester, on_delete=models.CASCADE, related_name='assessment_items')

    class Meta:
        verbose_name = "Assessment Item"
        verbose_name_plural = "Assessment Items"
        ordering = ['trimester', 'date', 'name']

    def __str__(self):
        return f"{self.name} - {self.subject.name} ({self.course.name})"