from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.authentication'
    
    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        
        post_migrate.connect(self.create_default_groups, sender=self)
    
    def create_default_groups(self, sender, **kwargs):
        """Create default groups with appropriate permissions."""
        from django.contrib.auth.models import Group, Permission
        
        admin_group, _ = Group.objects.get_or_create(name='Administrator')
        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        student_group, _ = Group.objects.get_or_create(name='Student')
        parent_group, _ = Group.objects.get_or_create(name='Parent')
        
        all_perms = Permission.objects.all()
        admin_group.permissions.set(all_perms)
        
        teacher_perms = Permission.objects.filter(
            codename__in=[
                'view_student', 'add_grade', 'change_grade', 'view_grade',
                'add_attendance', 'change_attendance', 'view_attendance',
                'add_participation', 'change_participation', 'view_participation',
                'view_subject'
            ]
        )
        teacher_group.permissions.set(teacher_perms)
        
        student_perms = Permission.objects.filter(
            codename__in=[
                'view_grade', 'view_attendance', 'view_participation',
                'view_subject'
            ]
        )
        student_group.permissions.set(student_perms)
        
        parent_perms = Permission.objects.filter(
            codename__in=[
                'view_grade', 'view_attendance', 'view_participation',
                'view_subject'
            ]
        )
        parent_group.permissions.set(parent_perms)