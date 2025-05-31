import random
from datetime import timedelta, date
import time

from django.core.management.base import BaseCommand
from django.db import transaction, utils as db_utils
from faker import Faker

from app.authentication.models import Student
from app.academic.models import (
    Period, Course, Subject, Trimester,
    Enrollment, AssessmentItem, Grade, Participation # Added Participation
)

# Configuration
NUM_FIXED_EXAMS_PER_TRIMESTER = 3
NUM_TASKS_PER_TRIMESTER = 3
GRADES_MIN = 50
GRADES_MAX = 100
GRADE_BATCH_SIZE = 500

NUM_PARTICIPATIONS_PER_TRIMESTER_SUBJECT = 5 # Number of participation records per student/subject/trimester
PARTICIPATION_BATCH_SIZE = 500

class Command(BaseCommand):
    help = 'Populates Trimesters, structured AssessmentItems, Grades, and Participations for existing academic data.'

    def _create_grades_for_assessment_item(self, student, assessment_item, period, subject, grades_to_create_list):
        grades_to_create_list.append(
            Grade(
                student=student,
                assessment_item=assessment_item,
                value=random.randint(GRADES_MIN, GRADES_MAX),
                subject=subject,
                period=period
            )
        )

    def _create_participations_for_trimester_subject(self, student, course, subject, period, trimester_start, trimester_end, participations_to_create_list, fake_instance):
        for _ in range(NUM_PARTICIPATIONS_PER_TRIMESTER_SUBJECT):
            try:
                # Ensure date is within trimester bounds
                days_in_trimester = (trimester_end - trimester_start).days
                if days_in_trimester < 0: days_in_trimester = 0 # Handle edge case if end < start
                
                random_day_offset = random.randint(0, days_in_trimester)
                participation_date = trimester_start + timedelta(days=random_day_offset)
                
                # Ensure participation_date does not exceed trimester_end
                if participation_date > trimester_end:
                    participation_date = trimester_end

            except ValueError: # Fallback if date generation fails
                participation_date = trimester_start
            
            participations_to_create_list.append(
                Participation(
                    student=student,
                    course=course,
                    subject=subject,
                    period=period, # Period of the trimester
                    date=participation_date,
                    level=random.choice([level[0] for level in Participation.PARTICIPATION_LEVELS]),
                    comments=fake_instance.sentence() if random.random() < 0.15 else ""
                )
            )


    def handle(self, *args, **options):
        fake = Faker('es_ES')
        self.stdout.write(self.style.SUCCESS('Starting population of academic details (including participations)...'))

        existing_periods = Period.objects.all().order_by('start_date')
        if not existing_periods.exists():
            self.stdout.write(self.style.ERROR('No existing Periods found. Please populate Periods first.'))
            return

        for period in existing_periods:
            self.stdout.write(self.style.SUCCESS(f'Processing Period: {period.name} [{period.start_date} to {period.end_date}]'))
            
            try:
                with transaction.atomic(): # Transacción por cada PERIODO
                    trimesters_for_period = []
                    days_in_period = (period.end_date - period.start_date).days
                    trimester_duration_days = max(30, days_in_period // 3) if days_in_period >= 90 else max(1, days_in_period //3)

                    for i in range(3):
                        tr_name_suffix = period.name.split(' ')[-1] if ' ' in period.name else str(period.start_date.year)
                        tr_name = f"Trimestre {i+1} ({tr_name_suffix})"
                        
                        tr_start_date = period.start_date + timedelta(days=i * trimester_duration_days)
                        if i < 2:
                            tr_end_date = period.start_date + timedelta(days=((i + 1) * trimester_duration_days) - 1)
                        else:
                            tr_end_date = period.end_date

                        if tr_end_date < tr_start_date:
                            tr_end_date = tr_start_date + timedelta(days=max(0, trimester_duration_days -1))
                        if tr_end_date > period.end_date:
                            tr_end_date = period.end_date

                        trimester, created = Trimester.objects.get_or_create(
                            name=tr_name, period=period,
                            defaults={'start_date': tr_start_date, 'end_date': tr_end_date}
                        )
                        if not created and (trimester.start_date != tr_start_date or trimester.end_date != tr_end_date) :
                            trimester.start_date = tr_start_date
                            trimester.end_date = tr_end_date
                            trimester.save()
                            self.stdout.write(self.style.NOTICE(f'  Updated Trimester: {trimester.name} [{trimester.start_date} to {trimester.end_date}]'))
                        elif created:
                             self.stdout.write(self.style.SUCCESS(f'  Created Trimester: {trimester.name} [{trimester.start_date} to {trimester.end_date}]'))
                        trimesters_for_period.append(trimester)

                    enrollments_in_period = Enrollment.objects.filter(period=period, status='active').select_related('student__user', 'course', 'subject')
                    if not enrollments_in_period.exists():
                        self.stdout.write(self.style.WARNING(f'  No active enrollments found for period {period.name}.'))
                        continue
                    
                    self.stdout.write(self.style.SUCCESS(f'  Found {enrollments_in_period.count()} active enrollments for period {period.name}. Processing...'))
                    
                    grades_to_create_batch = []
                    participations_to_create_batch = [] # Batch for participations

                    for enrollment_idx, enrollment in enumerate(enrollments_in_period):
                        student = enrollment.student
                        course = enrollment.course
                        subject = enrollment.subject

                        if enrollment_idx > 0 and enrollment_idx % 50 == 0:
                             self.stdout.write(self.style.NOTICE(f'    Processed {enrollment_idx} enrollments for period {period.name}...'))

                        for trimester_obj in trimesters_for_period:
                            # Crear AssessmentItems (Exámenes) y sus Grades
                            exam_names = ["Examen Parcial 1", "Examen Parcial 2", "Examen Final"]
                            for j in range(NUM_FIXED_EXAMS_PER_TRIMESTER):
                                exam_name_full = exam_names[j % len(exam_names)]
                                assessment_name = f"{exam_name_full} - {subject.name} - {trimester_obj.name}"
                                try:
                                    exam_date_offset_days = (j + 1) * ( (trimester_obj.end_date - trimester_obj.start_date).days // (NUM_FIXED_EXAMS_PER_TRIMESTER + 1) )
                                    exam_date = trimester_obj.start_date + timedelta(days=max(0, exam_date_offset_days))
                                    if exam_date > trimester_obj.end_date: exam_date = trimester_obj.end_date
                                    if exam_date < trimester_obj.start_date: exam_date = trimester_obj.start_date
                                except ValueError: exam_date = trimester_obj.start_date

                                assessment_item, ai_created = AssessmentItem.objects.get_or_create(
                                    name=assessment_name, subject=subject, course=course, trimester=trimester_obj, assessment_type='EXAM',
                                    defaults={'date': exam_date, 'max_score': 100}
                                )
                                self._create_grades_for_assessment_item(student, assessment_item, period, subject, grades_to_create_batch)

                            # Crear AssessmentItems (Tareas) y sus Grades
                            for k in range(NUM_TASKS_PER_TRIMESTER):
                                task_name_full = f"Tarea Práctica {k+1}"
                                assessment_name = f"{task_name_full} - {subject.name} - {trimester_obj.name}"
                                try:
                                    task_date_offset_days = (k + 1) * ( (trimester_obj.end_date - trimester_obj.start_date).days // (NUM_TASKS_PER_TRIMESTER + 2) )
                                    task_date = trimester_obj.start_date + timedelta(days=max(0, task_date_offset_days))
                                    if task_date > trimester_obj.end_date: task_date = trimester_obj.end_date
                                    if task_date < trimester_obj.start_date: task_date = trimester_obj.start_date
                                except ValueError: task_date = trimester_obj.start_date
                                
                                assessment_item, ai_created = AssessmentItem.objects.get_or_create(
                                    name=assessment_name, subject=subject, course=course, trimester=trimester_obj, assessment_type='TASK',
                                    defaults={'date': task_date, 'max_score': 100}
                                )
                                self._create_grades_for_assessment_item(student, assessment_item, period, subject, grades_to_create_batch)
                            
                            # Crear Participations para este estudiante, materia, en este trimestre
                            self._create_participations_for_trimester_subject(
                                student, course, subject, period, # period es el periodo del trimester_obj
                                trimester_obj.start_date, trimester_obj.end_date,
                                participations_to_create_batch, fake
                            )

                            # Procesar lotes si alcanzan el tamaño
                            if len(grades_to_create_batch) >= GRADE_BATCH_SIZE:
                                self.stdout.write(self.style.NOTICE(f'    Creating {len(grades_to_create_batch)} grades in batch for period {period.name}...'))
                                Grade.objects.bulk_create(grades_to_create_batch, ignore_conflicts=True)
                                grades_to_create_batch = []
                            
                            if len(participations_to_create_batch) >= PARTICIPATION_BATCH_SIZE:
                                self.stdout.write(self.style.NOTICE(f'    Creating {len(participations_to_create_batch)} participations in batch for period {period.name}...'))
                                Participation.objects.bulk_create(participations_to_create_batch, ignore_conflicts=True)
                                participations_to_create_batch = []

                    # Crear los registros restantes en los lotes finales para el periodo
                    if grades_to_create_batch:
                        self.stdout.write(self.style.NOTICE(f'    Creating final {len(grades_to_create_batch)} grades in batch for period {period.name}...'))
                        Grade.objects.bulk_create(grades_to_create_batch, ignore_conflicts=True)
                    if participations_to_create_batch:
                        self.stdout.write(self.style.NOTICE(f'    Creating final {len(participations_to_create_batch)} participations in batch for period {period.name}...'))
                        Participation.objects.bulk_create(participations_to_create_batch, ignore_conflicts=True)
                    
                    self.stdout.write(self.style.SUCCESS(f'  Successfully processed and committed data for Period: {period.name}'))

            except db_utils.OperationalError as e:
                self.stdout.write(self.style.ERROR(f'DATABASE OPERATIONAL ERROR during processing of Period {period.name}: {e}'))
                self.stdout.write(self.style.ERROR('  Skipping this period. Data for this period might not be saved.'))
                time.sleep(10) 
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'UNEXPECTED ERROR during processing of Period {period.name}: {e}'))
                self.stdout.write(self.style.ERROR(f'  Skipping this period. Data for this period might not be saved. Traceback:'))
                import traceback
                self.stdout.write(traceback.format_exc())
                time.sleep(5)
                continue

        self.stdout.write(self.style.SUCCESS('Population of academic details (including participations) completed for all processable periods.'))