from django.db import models
from core.models.base_model import TimestampedModel

class Period(TimestampedModel):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name