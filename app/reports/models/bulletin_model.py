from django.db import models
from django.utils.text import slugify
from core.models.base_model import TimestampedModel
from app.authentication.models import Student
from app.academic.models import Trimester
import os
from base.storage import PublicMediaStorage

def bulletin_file_upload_path(instance, filename):
    bulletin = instance.bulletin
    student_id_slug = slugify(bulletin.student.student_id if bulletin.student.student_id else str(bulletin.student.pk))
    trimester_name_slug = slugify(bulletin.trimester.name)
    
    period_year = "unknown_year"
    if bulletin.trimester and bulletin.trimester.period and bulletin.trimester.period.start_date:
        period_year = str(bulletin.trimester.period.start_date.year)
    
    extension_map = {
        'pdf': 'pdf',
        'excel': 'xlsx',
        'html': 'html'
    }
    extension = extension_map.get(instance.format.lower(), 'pdf')
    
    final_filename = f"bulletin_{bulletin.pk}_{instance.format.upper()}_{student_id_slug}.{extension}"
    
    return os.path.join(
        period_year, 
        student_id_slug,
        trimester_name_slug,
        final_filename
    )

class Bulletin(TimestampedModel):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        GENERATING = 'GENERATING', 'Generating'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bulletins')
    trimester = models.ForeignKey(Trimester, on_delete=models.CASCADE, related_name='bulletins')
    
    overall_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grades_data = models.JSONField(default=dict, help_text="Snapshot of grades and subject averages")
    
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    
    generated_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Student Bulletin"
        verbose_name_plural = "Student Bulletins"
        unique_together = ('student', 'trimester')
        ordering = ['-trimester__start_date', 'student__user__last_name']

    def __str__(self):
        return f"Bulletin for {self.student.user.get_full_name()} - {self.trimester.name}"

    def school_year_at_generation(self):
        if self.trimester and self.trimester.period:
            return self.trimester.period.name.split(' ')[-1]
        return "unknown_year"

class BulletinFile(TimestampedModel):
    class FormatChoices(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel'
        HTML = 'html', 'HTML'

    bulletin = models.ForeignKey('Bulletin', on_delete=models.CASCADE, related_name='files')
    format = models.CharField(max_length=10, choices=FormatChoices.choices)
    file = models.FileField(
        storage=PublicMediaStorage(custom_path='bulletins'),
        upload_to=bulletin_file_upload_path
    )
    
    class Meta:
        verbose_name = "Bulletin File"
        verbose_name_plural = "Bulletin Files"
        unique_together = ('bulletin', 'format')
        ordering = ['bulletin', 'format']

    def __str__(self):
        return f"{self.bulletin} - {self.get_format_display()}"

    @property
    def url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        return None