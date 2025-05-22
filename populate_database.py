# populate_database.py
import os
import django
import random
from datetime import date, timedelta

# Configuración Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth.models import Group
from app.authentication.models import User, Student, Teacher
from app.academic.models import Course, Period, Subject, TeacherAssignment, Enrollment, Grade, Attendance

print("Iniciando población de la base de datos...")

# Crear o verificar grupos
grupos = {}
for nombre in ['Administrator', 'Teacher', 'Student', 'Parent']:
    grupos[nombre] = Group.objects.get_or_create(name=nombre)[0]
    print(f"Grupo {nombre} disponible")

# Crear periodos académicos
periodos = [
    {
        'name': 'Año Escolar 2024', 
        'start_date': date(2024, 2, 1), 
        'end_date': date(2024, 11, 30), 
        'is_active': False
    },
    {
        'name': 'Año Escolar 2025', 
        'start_date': date(2025, 2, 1), 
        'end_date': date(2025, 11, 30), 
        'is_active': True
    },
]

periodos_obj = []
for p_data in periodos:
    periodo, created = Period.objects.get_or_create(name=p_data['name'], defaults=p_data)
    if not created:
        for key, value in p_data.items():
            setattr(periodo, key, value)
        periodo.save()
    periodos_obj.append(periodo)
    print(f"Periodo {periodo.name} {'creado' if created else 'actualizado'}")

periodo_actual = Period.objects.get(is_active=True)

# Crear cursos (grados escolares)
cursos = [
    # Primaria
    {'name': '1ro de Primaria', 'code': 'P1', 'year': 2025, 'capacity': 30},
    {'name': '2do de Primaria', 'code': 'P2', 'year': 2025, 'capacity': 30},
    {'name': '3ro de Primaria', 'code': 'P3', 'year': 2025, 'capacity': 30},
    {'name': '4to de Primaria', 'code': 'P4', 'year': 2025, 'capacity': 30},
    {'name': '5to de Primaria', 'code': 'P5', 'year': 2025, 'capacity': 30},
    {'name': '6to de Primaria', 'code': 'P6', 'year': 2025, 'capacity': 30},
    # Secundaria
    {'name': '1ro de Secundaria', 'code': 'S1', 'year': 2025, 'capacity': 35},
    {'name': '2do de Secundaria', 'code': 'S2', 'year': 2025, 'capacity': 35},
    {'name': '3ro de Secundaria', 'code': 'S3', 'year': 2025, 'capacity': 35},
    {'name': '4to de Secundaria', 'code': 'S4', 'year': 2025, 'capacity': 35},
    {'name': '5to de Secundaria', 'code': 'S5', 'year': 2025, 'capacity': 35},
    {'name': '6to de Secundaria', 'code': 'S6', 'year': 2025, 'capacity': 35},
]

cursos_obj = []
for c_data in cursos:
    curso, created = Course.objects.get_or_create(code=c_data['code'], year=c_data['year'], defaults=c_data)
    if not created:
        for key, value in c_data.items():
            setattr(curso, key, value)
        curso.save()
    cursos_obj.append(curso)
    print(f"Curso {curso.name} {'creado' if created else 'actualizado'}")

# Crear materias
materias = [
    # Materias para primaria y secundaria
    {'name': 'Matemáticas', 'code': 'MAT', 'credit_hours': 5},
    {'name': 'Lenguaje', 'code': 'LEN', 'credit_hours': 5},
    {'name': 'Ciencias Naturales', 'code': 'CNT', 'credit_hours': 4},
    {'name': 'Ciencias Sociales', 'code': 'CSO', 'credit_hours': 4},
    {'name': 'Educación Física', 'code': 'EFI', 'credit_hours': 2},
    {'name': 'Música', 'code': 'MUS', 'credit_hours': 2},
    {'name': 'Artes Plásticas', 'code': 'ART', 'credit_hours': 2},
    {'name': 'Religión', 'code': 'REL', 'credit_hours': 2},
    
    # Materias solo para secundaria
    {'name': 'Física', 'code': 'FIS', 'credit_hours': 4},
    {'name': 'Química', 'code': 'QUI', 'credit_hours': 4},
    {'name': 'Biología', 'code': 'BIO', 'credit_hours': 4},
    {'name': 'Historia', 'code': 'HIS', 'credit_hours': 3},
    {'name': 'Geografía', 'code': 'GEO', 'credit_hours': 3},
    {'name': 'Educación Cívica', 'code': 'CIV', 'credit_hours': 2},
    {'name': 'Inglés', 'code': 'ING', 'credit_hours': 3},
    {'name': 'Informática', 'code': 'INF', 'credit_hours': 2},
]

materias_obj = []
for m_data in materias:
    materia, created = Subject.objects.get_or_create(code=m_data['code'], defaults=m_data)
    if not created:
        for key, value in m_data.items():
            setattr(materia, key, value)
        materia.save()
    materias_obj.append(materia)
    print(f"Materia {materia.name} {'creada' if created else 'actualizada'}")

materias_primaria = materias_obj[:8]  # Las primeras 8 materias
materias_secundaria = materias_obj     # Todas las materias para secundaria

# Crear administrador si no existe
admin_user, created = User.objects.get_or_create(
    email='admin@example.com',
    defaults={
        'first_name': 'Admin',
        'last_name': 'Principal',
        'is_staff': True,
        'is_superuser': True
    }
)

if created:
    admin_user.set_password('admin123')
    admin_user.save()
    admin_user.groups.add(grupos['Administrator'])
    print("Usuario administrador creado")
else:
    print("Usuario administrador ya existe")

# Crear profesores
profesores_data = [
    {
        'email': 'juanperez@example.com',
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'teacher_id': 'T001',
        'specialization': 'Matemáticas',
        'years_of_experience': 10,
        'date_joined': date(2015, 2, 1),
    },
    {
        'email': 'mariagonzales@example.com',
        'first_name': 'María',
        'last_name': 'Gonzales',
        'teacher_id': 'T002',
        'specialization': 'Lenguaje',
        'years_of_experience': 8,
        'date_joined': date(2017, 2, 1),
    },
    {
        'email': 'carlosmedina@example.com',
        'first_name': 'Carlos',
        'last_name': 'Medina',
        'teacher_id': 'T003',
        'specialization': 'Ciencias Naturales',
        'years_of_experience': 5,
        'date_joined': date(2020, 2, 1),
    },
    {
        'email': 'anamartinez@example.com',
        'first_name': 'Ana',
        'last_name': 'Martínez',
        'teacher_id': 'T004',
        'specialization': 'Ciencias Sociales',
        'years_of_experience': 12,
        'date_joined': date(2013, 2, 1),
    },
    {
        'email': 'robertosuarez@example.com',
        'first_name': 'Roberto',
        'last_name': 'Suárez',
        'teacher_id': 'T005',
        'specialization': 'Educación Física',
        'years_of_experience': 7,
        'date_joined': date(2018, 2, 1),
    },
    {
        'email': 'patriciaflores@example.com',
        'first_name': 'Patricia',
        'last_name': 'Flores',
        'teacher_id': 'T006',
        'specialization': 'Música',
        'years_of_experience': 4,
        'date_joined': date(2021, 2, 1),
    },
    {
        'email': 'gabrielrojas@example.com',
        'first_name': 'Gabriel',
        'last_name': 'Rojas',
        'teacher_id': 'T007',
        'specialization': 'Artes Plásticas',
        'years_of_experience': 6,
        'date_joined': date(2019, 2, 1),
    },
    {
        'email': 'luismorales@example.com',
        'first_name': 'Luis',
        'last_name': 'Morales',
        'teacher_id': 'T008',
        'specialization': 'Religión',
        'years_of_experience': 15,
        'date_joined': date(2010, 2, 1),
    },
    {
        'email': 'beatrizvargas@example.com',
        'first_name': 'Beatriz',
        'last_name': 'Vargas',
        'teacher_id': 'T009',
        'specialization': 'Física',
        'years_of_experience': 9,
        'date_joined': date(2016, 2, 1),
    },
    {
        'email': 'ramoncastro@example.com',
        'first_name': 'Ramón',
        'last_name': 'Castro',
        'teacher_id': 'T010',
        'specialization': 'Química',
        'years_of_experience': 11,
        'date_joined': date(2014, 2, 1),
    },
    {
        'email': 'luciamendez@example.com',
        'first_name': 'Lucía',
        'last_name': 'Méndez',
        'teacher_id': 'T011',
        'specialization': 'Biología',
        'years_of_experience': 6,
        'date_joined': date(2019, 2, 1),
    },
    {
        'email': 'fernandoquispe@example.com',
        'first_name': 'Fernando',
        'last_name': 'Quispe',
        'teacher_id': 'T012',
        'specialization': 'Historia',
        'years_of_experience': 8,
        'date_joined': date(2017, 2, 1),
    },
    {
        'email': 'veronicachoque@example.com',
        'first_name': 'Verónica',
        'last_name': 'Choque',
        'teacher_id': 'T013',
        'specialization': 'Geografía',
        'years_of_experience': 7,
        'date_joined': date(2018, 2, 1),
    },
    {
        'email': 'danielmamani@example.com',
        'first_name': 'Daniel',
        'last_name': 'Mamani',
        'teacher_id': 'T014',
        'specialization': 'Educación Cívica',
        'years_of_experience': 5,
        'date_joined': date(2020, 2, 1),
    },
    {
        'email': 'sandrarivera@example.com',
        'first_name': 'Sandra',
        'last_name': 'Rivera',
        'teacher_id': 'T015',
        'specialization': 'Inglés',
        'years_of_experience': 10,
        'date_joined': date(2015, 2, 1),
    },
    {
        'email': 'javierterrazas@example.com',
        'first_name': 'Javier',
        'last_name': 'Terrazas',
        'teacher_id': 'T016',
        'specialization': 'Informática',
        'years_of_experience': 6,
        'date_joined': date(2019, 2, 1),
    },
]

profesores_obj = []
for p_data in profesores_data:
    email = p_data['email']
    teacher_id = p_data['teacher_id']
    
    # Crear o actualizar usuario
    user_data = {
        'first_name': p_data['first_name'],
        'last_name': p_data['last_name'],
    }
    
    user, user_created = User.objects.get_or_create(email=email, defaults=user_data)
    
    if user_created:
        user.set_password('password123')
        user.save()
        user.groups.add(grupos['Teacher'])
    
    # Crear o actualizar perfil de profesor
    teacher_data = {
        'specialization': p_data['specialization'],
        'years_of_experience': p_data['years_of_experience'],
        'date_joined': p_data['date_joined'],
    }
    
    profesor, created = Teacher.objects.get_or_create(
        teacher_id=teacher_id, 
        user=user,
        defaults=teacher_data
    )
    
    if not created:
        for key, value in teacher_data.items():
            setattr(profesor, key, value)
        profesor.save()
    
    profesores_obj.append(profesor)
    print(f"Profesor {profesor.user.full_name} {'creado' if created else 'actualizado'}")

# Asignar profesores a materias y cursos
print("Asignando profesores a cursos y materias...")

# Primero limpiar asignaciones actuales para el periodo actual
TeacherAssignment.objects.filter(period=periodo_actual).delete()

# Asignar profesores según especialización
for profesor in profesores_obj:
    # Buscar materias que coincidan con la especialización
    materia_principal = next((m for m in materias_obj if m.name == profesor.specialization), None)
    
    if materia_principal:
        # Determinar a qué cursos puede enseñar esta materia
        cursos_posibles = cursos_obj
        if materia_principal.name in ['Física', 'Química', 'Biología', 'Historia', 'Geografía', 'Educación Cívica', 'Inglés', 'Informática']:
            cursos_posibles = cursos_obj[6:]  # Solo cursos de secundaria
        
        # Asignar esta materia a 2-4 cursos
        num_cursos = random.randint(2, min(4, len(cursos_posibles)))
        cursos_seleccionados = random.sample(cursos_posibles, num_cursos)
        
        for curso in cursos_seleccionados:
            TeacherAssignment.objects.create(
                teacher=profesor,
                course=curso,
                subject=materia_principal,
                period=periodo_actual,
                is_primary=True
            )
            print(f"Asignado {profesor.user.full_name} a {curso.name} - {materia_principal.name}")

# Asegurar que todas las combinaciones de curso-materia tengan un profesor
for curso in cursos_obj:
    # Determinar materias aplicables a este curso
    if curso.code.startswith('P'):  # Primaria
        materias_aplicables = materias_primaria
    else:  # Secundaria
        materias_aplicables = materias_secundaria
    
    # Verificar cada materia
    for materia in materias_aplicables:
        # ¿Ya tiene un profesor asignado?
        tiene_profesor = TeacherAssignment.objects.filter(
            course=curso,
            subject=materia,
            period=periodo_actual
        ).exists()
        
        if not tiene_profesor:
            # Asignar un profesor aleatorio
            profesor_aleatorio = random.choice(profesores_obj)
            
            TeacherAssignment.objects.create(
                teacher=profesor_aleatorio,
                course=curso,
                subject=materia,
                period=periodo_actual,
                is_primary=True
            )
            print(f"Asignado {profesor_aleatorio.user.full_name} a {curso.name} - {materia.name} (asignación faltante)")

# Crear estudiantes (15-25 por curso)
print("Creando estudiantes...")

nombres = ['José', 'Carlos', 'Luis', 'Juan', 'Pedro', 'Miguel', 'David', 'Fernando', 'Roberto', 'Jorge',
          'Ana', 'María', 'Laura', 'Sofía', 'Valentina', 'Camila', 'Lucía', 'Isabella', 'Daniela', 'Gabriela',
          'Diego', 'Sergio', 'Pablo', 'Mario', 'Adrián', 'Gabriel', 'Andrés', 'Javier', 'Alejandro', 'Emilio',
          'Patricia', 'Claudia', 'Isabel', 'Paula', 'Alejandra', 'Natalia', 'Carmen', 'Valeria', 'Rosa', 'Silvia']

apellidos = ['Sánchez', 'Rodríguez', 'López', 'Martínez', 'Pérez', 'Gómez', 'Flores', 'García', 'González', 'Hernández',
            'Mendoza', 'Vargas', 'Romero', 'Torres', 'Morales', 'Ortega', 'Núñez', 'Castro', 'Ríos', 'Medina',
            'Rojas', 'Chávez', 'Cruz', 'Vega', 'Reyes', 'Gutiérrez', 'Navarro', 'Ramos', 'Salazar', 'Jiménez',
            'Suárez', 'Molina', 'Cabrera', 'Herrera', 'Benítez', 'Acosta', 'Miranda', 'Fuentes', 'Aguilar', 'Espinoza']

contador_estudiantes = 0

# Limpiar inscripciones y calificaciones existentes para el periodo actual
Enrollment.objects.filter(period=periodo_actual).delete()
Grade.objects.filter(period=periodo_actual).delete()

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
        
        # Crear o actualizar usuario
        user_data = {
            'first_name': nombre,
            'last_name': apellido,
        }
        
        user, user_created = User.objects.get_or_create(email=email, defaults=user_data)
        
        if user_created:
            user.set_password('password123')
            user.save()
            user.groups.add(grupos['Student'])
        
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
            'enrollment_date': date(2025 - int(grado_num), 2, 1),
            'parent_name': f"{nombre_padre} {apellido}",
            'parent_contact': f"7{random.randint(1000000, 9999999)}",
            'parent_email': f"{nombre_padre.lower()}.{apellido.lower()}{contador_estudiantes}@example.com",
            'emergency_contact': f"7{random.randint(1000000, 9999999)}"
        }
        
        estudiante, created = Student.objects.get_or_create(
            student_id=student_id,
            user=user,
            defaults=student_data
        )
        
        if not created:
            for key, value in student_data.items():
                setattr(estudiante, key, value)
            estudiante.save()
        
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
            
            # Generar algunas asistencias
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
        
        if created:
            print(f"Estudiante creado: {estudiante.user.full_name} ({student_id})")
        else:
            print(f"Estudiante actualizado: {estudiante.user.full_name} ({student_id})")

# Resumen final
print("\nResumen de datos creados:")
print(f"- {Period.objects.count()} periodos académicos")
print(f"- {Course.objects.count()} cursos")
print(f"- {Subject.objects.count()} materias")
print(f"- {User.objects.count()} usuarios")
print(f"- {Teacher.objects.count()} profesores")
print(f"- {Student.objects.count()} estudiantes")
print(f"- {TeacherAssignment.objects.count()} asignaciones de profesores")
print(f"- {Enrollment.objects.count()} inscripciones")
print(f"- {Grade.objects.count()} calificaciones")
print(f"- {Attendance.objects.count()} registros de asistencia")
print("\nPoblación de datos completada con éxito!")