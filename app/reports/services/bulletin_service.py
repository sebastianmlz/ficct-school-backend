from django.utils import timezone
from django.db import transaction
from django.db.models import Avg
from django.core.files.base import ContentFile
from app.authentication.models import Student
from app.academic.models import Trimester, Grade, Subject
from app.reports.models.bulletin_model import Bulletin, BulletinFile
from app.reports.services.pdf_service import pdf_bulletin_service
from app.reports.services.excel_service import excel_bulletin_service
from app.reports.services.html_service import html_bulletin_service
from core.models import LoggerService
import logging

logger = logging.getLogger(__name__)

class BulletinService:

    def _collect_student_trimester_data(self, student: Student, trimester: Trimester):
        subjects_in_trimester = Subject.objects.filter(
            assessment_items__trimester=trimester,
            assessment_items__grades__student=student
        ).distinct()

        grades_details = {'subjects': []}
        total_subject_averages = []

        for subject in subjects_in_trimester:
            subject_grades = Grade.objects.filter(
                student=student,
                assessment_item__trimester=trimester,
                assessment_item__subject=subject
            ).select_related('assessment_item')

            if not subject_grades.exists():
                continue

            subject_average = subject_grades.aggregate(avg=Avg('value'))['avg'] or 0
            total_subject_averages.append(subject_average)

            assessments_data = []
            for grade in subject_grades:
                assessments_data.append({
                    'name': grade.assessment_item.name,
                    'date': grade.assessment_item.date.isoformat() if grade.assessment_item.date else None,
                    'grade_value': float(grade.value),
                    'max_score': float(grade.assessment_item.max_score),
                })
            
            grades_details['subjects'].append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'subject_average': float(subject_average),
                'assessments': assessments_data,
            })
        
        overall_trimester_average = sum(total_subject_averages) / len(total_subject_averages) if total_subject_averages else 0
        grades_details['overall_average'] = float(overall_trimester_average)
        
        return grades_details

    def _save_bulletin_file(self, bulletin_instance, file_format, content_bytes, filename_suggestion):
        try:
            BulletinFile.objects.filter(bulletin=bulletin_instance, format=file_format).delete()
            
            bulletin_file = BulletinFile(bulletin=bulletin_instance, format=file_format)
            bulletin_file.file.save(filename_suggestion, ContentFile(content_bytes), save=True)
            return bulletin_file
        except Exception as e:
            logger.error(f"Error saving bulletin file {file_format}: {str(e)}", exc_info=True)
            raise

    @transaction.atomic
    def generate_bulletin_for_student_trimester(self, student_id: int, trimester_id: int, force_regenerate: bool = False, generating_user=None):
        try:
            student = Student.objects.get(pk=student_id)
            trimester = Trimester.objects.get(pk=trimester_id)
        except (Student.DoesNotExist, Trimester.DoesNotExist) as e:
            raise ValueError(f"Invalid student or trimester ID: {str(e)}")

        bulletin, created = Bulletin.objects.get_or_create(
            student=student,
            trimester=trimester,
            defaults={'status': Bulletin.StatusChoices.PENDING}
        )

        if not created and not force_regenerate and bulletin.status == Bulletin.StatusChoices.COMPLETED:
            LoggerService.objects.create(
                user=generating_user, action='BULLETIN_REQUEST_SKIPPED', level='INFO',
                table_name='Bulletin',
                description=f"Bulletin for {student.user.get_full_name()} - {trimester.name} already exists and regeneration not forced."
            )
            return bulletin, False

        bulletin.status = Bulletin.StatusChoices.GENERATING
        bulletin.error_message = None
        bulletin.save()
        
        LoggerService.objects.create(
            user=generating_user, action='BULLETIN_GENERATION_STARTED', level='INFO',
            table_name='Bulletin',
            description=f"Bulletin generation started for {student.user.get_full_name()} - {trimester.name}."
        )

        try:
            collected_data = self._collect_student_trimester_data(student, trimester)
            bulletin.grades_data = collected_data
            bulletin.overall_average = collected_data.get('overall_average', 0)
            bulletin.save(update_fields=['grades_data', 'overall_average'])

            html_bytes, html_filename = html_bulletin_service.generate_html_content(bulletin)
            self._save_bulletin_file(bulletin, BulletinFile.FormatChoices.HTML, html_bytes, html_filename)

            pdf_bytes, pdf_filename = pdf_bulletin_service.generate_pdf_content(bulletin)
            self._save_bulletin_file(bulletin, BulletinFile.FormatChoices.PDF, pdf_bytes, pdf_filename)

            excel_bytes, excel_filename = excel_bulletin_service.generate_excel_content(bulletin)
            self._save_bulletin_file(bulletin, BulletinFile.FormatChoices.EXCEL, excel_bytes, excel_filename)
            
            bulletin.status = Bulletin.StatusChoices.COMPLETED
            bulletin.generated_at = timezone.now()
            bulletin.save(update_fields=['status', 'generated_at'])
            LoggerService.objects.create(
                user=generating_user, action='BULLETIN_GENERATION_COMPLETED', level='SUCCESS',
                table_name='Bulletin',
                description=f"Bulletin successfully generated for {student.user.get_full_name()} - {trimester.name}."
            )
            return bulletin, True
        except Exception as e:
            logger.error(f"Error generating bulletin: {str(e)}", exc_info=True)
            bulletin.status = Bulletin.StatusChoices.FAILED
            bulletin.error_message = str(e)
            bulletin.save(update_fields=['status', 'error_message'])
            LoggerService.objects.create(
                user=generating_user, action='BULLETIN_GENERATION_FAILED', level='ERROR',
                table_name='Bulletin',
                description=f"Bulletin generation failed for {student.user.get_full_name()} - {trimester.name}. Error: {str(e)}"
            )
            raise

bulletin_service = BulletinService()