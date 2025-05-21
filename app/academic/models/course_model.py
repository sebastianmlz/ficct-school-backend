from django.db import models
from core.models.base_model import TimestampedModel

class Course(TimestampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)
    year = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.year})"
    
    class Meta:
        ordering = ['year', 'name']
        unique_together = ['name', 'year']