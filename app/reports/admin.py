from django.contrib import admin
from django.utils.html import format_html
from app.reports.models.bulletin_model import Bulletin, BulletinFile

class BulletinFileInline(admin.TabularInline):
    model = BulletinFile
    fields = ('format', 'file_link')
    readonly_fields = ('format', 'file_link')
    extra = 0
    can_delete = False

    def file_link(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            return format_html("<a href='{url}' target='_blank'>{filename}</a>", url=obj.file.url, filename=obj.file.name.split('/')[-1])
        return "No file"
    file_link.short_description = "File"


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'trimester_name', 'overall_average', 'status', 'generated_at', 'file_links')
    list_filter = ('status', 'trimester__period', 'trimester')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__student_id', 'trimester__name')
    readonly_fields = ('created_at', 'updated_at', 'generated_at', 'grades_data', 'error_message')
    inlines = [BulletinFileInline]
    
    fieldsets = (
        (None, {
            'fields': ('student', 'trimester', 'status', 'overall_average')
        }),
        ('Details (Read-Only)', {
            'fields': ('grades_data', 'generated_at', 'error_message', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'

    def trimester_name(self, obj):
        return f"{obj.trimester.name} ({obj.trimester.period.name})"
    trimester_name.short_description = 'Trimester'

    def file_links(self, obj):
        links = []
        for bf in obj.files.all():
            if bf.file and hasattr(bf.file, 'url'):
                links.append(format_html("<a href='{url}' target='_blank'>{format}</a>", url=bf.file.url, format=bf.get_format_display()))
        return format_html(" | ".join(links)) if links else "No files"
    file_links.short_description = "Generated Files"