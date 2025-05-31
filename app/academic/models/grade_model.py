from django.db import models
from core.models import TimestampedModel
from app.authentication.models import Student
from .subject_model import Subject
from .period_model import Period
from .assessment_item_model import AssessmentItem

class Grade(TimestampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='grades')
    assessment_item = models.ForeignKey(AssessmentItem, on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    value = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ['-date_recorded', 'student', 'subject']
        unique_together = ('student', 'assessment_item')

    def __str__(self):
        if self.assessment_item:
            return f"Grade for {self.student} in {self.assessment_item.name}: {self.value}"
        return f"Grade for {self.student} in {self.subject.name} ({self.period.name}): {self.value}"