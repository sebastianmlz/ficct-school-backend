from django.template import Template, Context
from app.reports.models.bulletin_model import Bulletin
from app.academic.models import Enrollment

class HTMLBulletinService:
    def generate_html_content(self, bulletin: Bulletin):
        student = bulletin.student
        trimester = bulletin.trimester
        course_name = "N/A"
        try:
            enrollment = Enrollment.objects.filter(
                student=student, 
                period=trimester.period,
                status='active'
            ).select_related('course').first()
            if enrollment and enrollment.course:
                course_name = enrollment.course.name
        except Enrollment.DoesNotExist:
            pass

        html_content = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Boletín de Calificaciones - {{ bulletin.trimester.name }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { margin: 0; color: #2c3e50; }
                .header p { margin: 5px 0; }
                .student-info { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9; }
                .student-info p { margin: 5px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #f2f2f2; color: #333; }
                .overall-average { font-weight: bold; font-size: 1.2em; margin-top: 20px; text-align: right; padding: 10px; }
                .footer { text-align: center; margin-top: 40px; font-size: 0.9em; color: #777; border-top: 1px solid #eee; padding-top: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Boletín de Calificaciones</h1>
                <p>Institución Educativa FICCT School</p>
                <p>{{ bulletin.trimester.period.name }} - {{ bulletin.trimester.name }}</p>
            </div>

            <div class="student-info">
                <p><strong>Estudiante:</strong> {{ bulletin.student.user.get_full_name }}</p>
                <p><strong>ID Estudiante:</strong> {{ bulletin.student.student_id }}</p>
                <p><strong>Curso:</strong> {{ course_name }}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Materia</th>
                        <th>Promedio</th>
                    </tr>
                </thead>
                <tbody>
                    {% for subject_data in bulletin.grades_data.subjects %}
                    <tr>
                        <td>{{ subject_data.subject_name }}</td>
                        <td>{{ subject_data.subject_average|floatformat:2 }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="overall-average">
                Promedio General: {{ bulletin.overall_average|floatformat:2 }}
            </div>

            <div class="footer">
                <p>Generado el: {{ bulletin.generated_at|date:"d/m/Y H:i" }}</p>
                <p>&copy; {{ bulletin.generated_at|date:"Y" }} FICCT School. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        
        context_data = {
            'bulletin': bulletin,
            'course_name': course_name,
        }
        
        template = Template(html_content)
        context = Context(context_data)
        rendered_html = template.render(context)
        
        filename = f"bulletin_{bulletin.pk}.html"
        return rendered_html.encode('utf-8'), filename

html_bulletin_service = HTMLBulletinService()