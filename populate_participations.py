#!/usr/bin/env python
import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from django.db import transaction
from app.authentication.models import Student
from app.academic.models import Course, Period, Subject, Enrollment, Participation, TeacherAssignment

def generate_participations():
    try:
        active_period = Period.objects.filter(is_active=True).first()
        if not active_period:
            active_period = Period.objects.order_by('-start_date').first()
        
        if not active_period:
            print("Error: No se encontraron periodos en la base de datos.")
            return
            
        print(f"Usando periodo: {active_period.name}")
        
        estudiantes = Student.objects.all()
        if not estudiantes:
            print("Error: No se encontraron estudiantes en la base de datos.")
            return
        
        print(f"Encontrados {estudiantes.count()} estudiantes.")
        
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(weeks=12)
        
        fechas_posibles = []
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() < 5:
                fechas_posibles.append(fecha_actual)
            fecha_actual += timedelta(days=1)
        
        niveles = ['high', 'medium', 'low', 'none']
        
        comentarios = {
            'high': [
                "Participación sobresaliente durante toda la clase",
                "Realizó aportes significativos al debate",
                "Respondió correctamente a todas las preguntas",
                "Mostró dominio del tema con ejemplos originales",
                "Ayudó a resolver dudas de otros compañeros"
            ],
            'medium': [
                "Participó cuando se le solicitó",
                "Aportó ideas relevantes al tema",
                "Respondió correctamente a la mayoría de preguntas",
                "Demostró interés en la materia",
                "Presentó un trabajo voluntario"
            ],
            'low': [
                "Participó solo cuando fue requerido directamente",
                "Sus aportes fueron mínimos",
                "Mostró cierta inseguridad al responder",
                "Demostró poco interés en el tema",
                "Se distrajo durante parte de la clase"
            ],
            'none': [
                "No participó durante la clase",
                "Estuvo distraído con el celular",
                "No mostró interés en las actividades",
                "Se negó a responder cuando se le preguntó",
                "No trajo el material solicitado"
            ]
        }
        
        total_participaciones = 0
        estudiantes_procesados = 0
        
        with transaction.atomic():
            for estudiante in estudiantes:
                try:
                    inscripciones = Enrollment.objects.filter(student=estudiante, period=active_period)
                    
                    if not inscripciones:
                        continue
                    
                    for inscripcion in inscripciones:
                        with transaction.atomic():
                            curso = inscripcion.course
                            asignaciones = TeacherAssignment.objects.filter(course=curso, period=active_period)
                            materia_ids = asignaciones.values_list('subject_id', flat=True).distinct()
                            materias = Subject.objects.filter(id__in=materia_ids)
                            
                            if not materias:
                                continue
                            
                            for materia in materias:
                                with transaction.atomic():
                                    num_participaciones = random.randint(2, 6)
                                    fechas_seleccionadas = random.sample(fechas_posibles, min(num_participaciones, len(fechas_posibles)))
                                    
                                    for fecha in fechas_seleccionadas:
                                        nivel = random.choice(niveles)
                                        comentario = random.choice(comentarios[nivel])
                                        
                                        exists = Participation.objects.filter(
                                            student=estudiante,
                                            course=curso,
                                            subject=materia,
                                            period=active_period,
                                            date=fecha
                                        ).exists()
                                        
                                        if not exists:
                                            Participation.objects.create(
                                                student=estudiante,
                                                course=curso,
                                                subject=materia,
                                                period=active_period,
                                                date=fecha,
                                                level=nivel,
                                                comments=comentario
                                            )
                                            total_participaciones += 1
                except Exception as e:
                    print(f"Error procesando estudiante: {str(e)}")
                    continue
                
                estudiantes_procesados += 1
                if estudiantes_procesados % 10 == 0:
                    print(f"Procesados {estudiantes_procesados}/{estudiantes.count()} estudiantes...")
        
        print(f"¡Completado! Se crearon {total_participaciones} registros de participación para {estudiantes_procesados} estudiantes.")
    except Exception as e:
        print(f"Error general: {str(e)}")
        return

if __name__ == "__main__":
    print("=== Script de población de registros de participación ===")
    generate_participations()
    print("Proceso finalizado.")