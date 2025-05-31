from django.db import models
from core.models import TimestampedModel
from .period_model import Period

class Trimester(TimestampedModel):
    name = models.CharField(max_length=100)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='trimesters')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        verbose_name = "Trimester"
        verbose_name_plural = "Trimesters"
        ordering = ['period', 'start_date']
        unique_together = ('name', 'period')

    def __str__(self):
        return f"{self.name} ({self.period.name})"