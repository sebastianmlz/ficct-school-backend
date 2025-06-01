from rest_framework import permissions
from app.authentication.models import Student, Teacher

class BulletinPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        if hasattr(request.user, 'teacher_profile'):
            return True
            
        if hasattr(request.user, 'student_profile'):
            return True
            
        return False
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        if hasattr(request.user, 'student_profile'):
            return obj.student.pk == request.user.student_profile.pk
            
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            
            from app.academic.models import TeacherAssignment, Enrollment
            
            teacher_assignments = TeacherAssignment.objects.filter(
                teacher=teacher
            ).values_list('course_id', 'period_id')
            
            student_enrollment = Enrollment.objects.filter(
                student=obj.student,
                period=obj.trimester.period,
                course_id__in=[assignment[0] for assignment in teacher_assignments]
            ).exists()
            
            return student_enrollment
            
        return False