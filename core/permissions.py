from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'teacher_profile')

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'student_profile')

class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'parent_profile')

class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or hasattr(request.user, 'teacher_profile'))
        )

class IsStudentOwnerOrTeacherOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or hasattr(request.user, 'teacher_profile'):
            return True
        
        if hasattr(obj, 'student'):
            return obj.student.user == request.user
        if hasattr(obj, 'user'):
             return obj.user == request.user
        if hasattr(obj, 'student_profile'):
            return obj == request.user and hasattr(request.user, 'student_profile')
            
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS