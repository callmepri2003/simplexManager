from django.contrib import admin
from .models import *

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1  # show one empty row for quick add

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0  # don't show empty rows since attendances are auto-created
    fields = ['tutoringStudent', 'present', 'homework', 'paid']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["group", "notes", "date"]
    inlines = [ResourceInline, AttendanceInline]


# Register other models normally
admin.site.register(Group)
admin.site.register(Attendance)
admin.site.register(Parent)
admin.site.register(TutoringStudent)