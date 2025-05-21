from django.db import models
from core.models.base_model import TimestampedModel

class TeacherAssignment(TimestampedModel):
    teacher = models.ForeignKey('authentication.Teacher', on_delete=models.CASCADE,
                               related_name='assignments')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE,
                              related_name='teacher_assignments')
    subject = models.ForeignKey('academic.Subject', on_delete=models.CASCADE,
                               related_name='teacher_assignments')
    period = models.ForeignKey('academic.Period', on_delete=models.CASCADE,
                              related_name='teacher_assignments')
    
    is_primary = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('teacher', 'course', 'subject', 'period')
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'subject', 'period'],
                condition=models.Q(is_primary=True),
                name='unique_primary_teacher'
            )
        ]
    
    def __str__(self):
        return f"{self.teacher} - {self.subject.name} at {self.course.name}"