import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from app.reports.models.bulletin_model import Bulletin
from app.academic.models import Enrollment

class PDFBulletinService:
    def generate_pdf_content(self, bulletin: Bulletin):
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

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=inch/2, leftMargin=inch/2, rightMargin=inch/2, bottomMargin=inch/2)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, spaceAfter=0.3*inch)
        header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=14, alignment=1, spaceAfter=0.1*inch)
        subheader_style = ParagraphStyle('SubHeader', parent=styles['Heading3'], fontSize=12, alignment=1, spaceAfter=0.3*inch)
        
        elements.append(Paragraph("Boletín de Calificaciones", title_style))
        elements.append(Paragraph("Institución Educativa FICCT School", header_style))
        elements.append(Paragraph(f"{trimester.period.name} - {trimester.name}", subheader_style))
        
        info_style = ParagraphStyle('Info', parent=styles['Normal'], spaceAfter=6)
        elements.append(Paragraph(f"<b>Estudiante:</b> {student.user.get_full_name()}", info_style))
        elements.append(Paragraph(f"<b>ID Estudiante:</b> {student.student_id}", info_style))
        elements.append(Paragraph(f"<b>Curso:</b> {course_name}", info_style))
        elements.append(Spacer(1, 0.3*inch))
        
        data = [["Materia", "Promedio"]]
        subjects_data = bulletin.grades_data.get('subjects', [])
        
        for subject in subjects_data:
            subject_name = subject.get('subject_name', '')
            subject_average = round(float(subject.get('subject_average', 0)), 2)
            data.append([subject_name, subject_average])
            
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        
        elements.append(Spacer(1, 0.3*inch))
        overall_style = ParagraphStyle('Overall', parent=styles['Heading4'], alignment=2)
        elements.append(Paragraph(f"Promedio General: {round(float(bulletin.overall_average or 0), 2)}", overall_style))
        
        elements.append(Spacer(1, 0.7*inch))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, fontSize=9)
        elements.append(Paragraph(f"Generado el: {bulletin.generated_at.strftime('%d/%m/%Y %H:%M') if bulletin.generated_at else 'N/A'}", footer_style))
        elements.append(Paragraph(f"© {trimester.period.start_date.year if trimester.period and trimester.period.start_date else '2025'} FICCT School. Todos los derechos reservados.", footer_style))
        
        doc.build(elements)
        buffer.seek(0)
        
        filename = f"bulletin_{bulletin.pk}.pdf"
        return buffer.getvalue(), filename

pdf_bulletin_service = PDFBulletinService()