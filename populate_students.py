# populate_students_fixed.py
import os
import django
import random
from datetime import date, timedelta

# Configuración Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth.models import Group
from app.authentication.models import User, Student
from app.academic.models import Course, Period, Subject, TeacherAssignment, Enrollment, Grade, Attendance

print("Iniciando población de estudiantes en la base de datos...")

# Obtener el último ID de estudiante para continuar la secuencia
ultimo_id = 0
if Student.objects.exists():
    ultimo_estudiante = Student.objects.all().order_by('-student_id').first()
    if ultimo_estudiante and '-' in ultimo_estudiante.student_id:
        try:
            ultimo_id = int(ultimo_estudiante.student_id.split('-')[1])
            print(f"Continuando desde el último ID de estudiante: {ultimo_id}")
        except ValueError:
            print(f"No se pudo determinar el último ID numérico, usando 0")

# Obtener datos existentes
periodo_actual = Period.objects.get(is_active=True)
cursos_obj = list(Course.objects.all().order_by('code'))
materias_obj = list(Subject.objects.all())
materias_primaria = list(Subject.objects.filter(code__in=['MAT', 'LEN', 'CNT', 'CSO', 'EFI', 'MUS', 'ART', 'REL']))
materias_secundaria = list(Subject.objects.all())
grupo_estudiante = Group.objects.get(name='Student')

# Informar sobre el entorno
print(f"Usando período activo: {periodo_actual.name}")
print(f"Encontrados {len(cursos_obj)} cursos")
print(f"Encontradas {len(materias_obj)} materias ({len(materias_primaria)} para primaria)")

# Limpiar inscripciones, calificaciones y asistencias existentes para el periodo actual
print("Limpiando datos parciales de estudiantes...")
Enrollment.objects.filter(period=periodo_actual).delete()
Grade.objects.filter(period=periodo_actual).delete()
Attendance.objects.filter(period=periodo_actual).delete()

# Nombres y apellidos para los estudiantes
nombres = ['José', 'Carlos', 'Luis', 'Juan', 'Pedro', 'Miguel', 'David', 'Fernando', 'Roberto', 'Jorge',
          'Ana', 'María', 'Laura', 'Sofía', 'Valentina', 'Camila', 'Lucía', 'Isabella', 'Daniela', 'Gabriela',
          'Diego', 'Sergio', 'Pablo', 'Mario', 'Adrián', 'Gabriel', 'Andrés', 'Javier', 'Alejandro', 'Emilio',
          'Patricia', 'Claudia', 'Isabel', 'Paula', 'Alejandra', 'Natalia', 'Carmen', 'Valeria', 'Rosa', 'Silvia']

apellidos = ['Sánchez', 'Rodríguez', 'López', 'Martínez', 'Pérez', 'Gómez', 'Flores', 'García', 'González', 'Hernández',
            'Mendoza', 'Vargas', 'Romero', 'Torres', 'Morales', 'Ortega', 'Núñez', 'Castro', 'Ríos', 'Medina',
            'Rojas', 'Chávez', 'Cruz', 'Vega', 'Reyes', 'Gutiérrez', 'Navarro', 'Ramos', 'Salazar', 'Jiménez',
            'Suárez', 'Molina', 'Cabrera', 'Herrera', 'Benítez', 'Acosta', 'Miranda', 'Fuentes', 'Aguilar', 'Espinoza']

contador_estudiantes = ultimo_id  # Iniciar desde el último ID encontrado
estudiantes_creados = 0
estudiantes_actualizados = 0

# Mapeo de los estudiantes existentes por ID para evitar duplicados
estudiantes_existentes = {
    estudiante.student_id: estudiante 
    for estudiante in Student.objects.all()
}

for curso in cursos_obj:
    # Determinar cuántos estudiantes para este curso (15-25)
    num_estudiantes = random.randint(15, min(25, curso.capacity))
    
    # Determinar materias para este curso
    if curso.code.startswith('P'):  # Primaria
        materias_curso = materias_primaria
    else:  # Secundaria
        materias_curso = materias_secundaria
    
    print(f"Creando {num_estudiantes} estudiantes para {curso.name}...")
    
    for i in range(num_estudiantes):
        contador_estudiantes += 1
        
        # Generar datos para el estudiante
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        
        # Email único
        email = f"{nombre.lower()}.{apellido.lower()}{contador_estudiantes}@example.com"
        
        # ID de estudiante único
        grado_prefijo = curso.code[0]  # P o S
        grado_num = curso.code[1]      # Número del grado
        student_id = f"{grado_prefijo}{grado_num}-{contador_estudiantes:03d}"
        
        # Verificar si ya existe un estudiante con este ID
        if student_id in estudiantes_existentes:
            # Si existe, continuar al siguiente
            print(f"  Saltando ID existente: {student_id}")
            continue
        
        # Crear el usuario
        user_data = {
            'first_name': nombre,
            'last_name': apellido,
        }
        
        user, user_created = User.objects.get_or_create(email=email, defaults=user_data)
        
        if user_created:
            user.set_password('password123')
            user.save()
            user.groups.add(grupo_estudiante)
        
        # Calcular fecha de nacimiento apropiada
        if curso.code.startswith('P'):
            edad = 5 + int(grado_num)  # 1ro = 6 años, etc.
        else:
            edad = 11 + int(grado_num)  # 1ro = 12 años, etc.
        
        nacimiento_anio = 2025 - edad
        nacimiento_mes = random.randint(1, 12)
        nacimiento_dia = random.randint(1, 28)
        
        if user_created:
            user.date_of_birth = date(nacimiento_anio, nacimiento_mes, nacimiento_dia)
            user.save()
        
        # Datos de los padres
        nombre_padre = random.choice(nombres)
        
        # Crear o actualizar perfil de estudiante
        student_data = {
            'user': user,
            'enrollment_date': date(2025 - int(grado_num), 2, 1),
            'parent_name': f"{nombre_padre} {apellido}",
            'parent_contact': f"7{random.randint(1000000, 9999999)}",
            'parent_email': f"{nombre_padre.lower()}.{apellido.lower()}{contador_estudiantes}@example.com",
            'emergency_contact': f"7{random.randint(1000000, 9999999)}"
        }
        
        # Crear estudiante directamente para evitar problemas de ID duplicado
        estudiante = Student.objects.create(
            student_id=student_id,
            **student_data
        )
        estudiantes_creados += 1
        print(f"  Estudiante creado: {estudiante.user.full_name} ({student_id})")
        
        # Inscribir estudiante en las materias del curso
        for materia in materias_curso:
            # Crear inscripción
            inscripcion = Enrollment.objects.create(
                student=estudiante,
                course=curso,
                subject=materia,
                period=periodo_actual,
                status='active'
            )
            
            # Generar calificación
            nota = random.randint(51, 100)  # Sistema boliviano: 51-100
            
            Grade.objects.create(
                student=estudiante,
                course=curso,
                subject=materia,
                period=periodo_actual,
                value=nota,
                comments="Calificación del primer trimestre"
            )
            
            # Generar algunas asistencias (máximo 5 días para no sobrecargar)
            for dia in range(1, 6):  # 5 días de asistencia
                fecha = date(2025, 5, dia)
                estado = random.choices(
                    ['present', 'absent', 'late', 'excused'],
                    weights=[85, 5, 8, 2],
                    k=1
                )[0]
                
                Attendance.objects.create(
                    student=estudiante,
                    course=curso,
                    subject=materia,
                    period=periodo_actual,
                    date=fecha,
                    status=estado
                )

# Resumen final
print("\nResumen de datos creados:")
print(f"- {estudiantes_creados} nuevos estudiantes")
print(f"- {Enrollment.objects.filter(period=periodo_actual).count()} inscripciones")
print(f"- {Grade.objects.filter(period=periodo_actual).count()} calificaciones")
print(f"- {Attendance.objects.filter(period=periodo_actual).count()} registros de asistencia")
print("\nPoblación de estudiantes completada con éxito!")