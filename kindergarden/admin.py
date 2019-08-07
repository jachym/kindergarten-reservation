from django.contrib import admin

from .models import Kindergarten, Teacher, Parent, Day, Child

class KindergartenAdmin(admin.ModelAdmin):
    pass

class TeacherAdmin(admin.ModelAdmin):
    pass

class ParentAdmin(admin.ModelAdmin):
    pass

class ChildAdmin(admin.ModelAdmin):
    pass

class ChildInline(admin.TabularInline):
    model = Child.days.through
    extra = 0

class TeachersInline(admin.TabularInline):
    model = Teacher.days.through
    extra = 0

class DayAdmin(admin.ModelAdmin):
    inlines = [
            ChildInline, TeachersInline
    ]
    exclude = ("days", "teachers")

admin.site.register(Kindergarten, KindergartenAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Day, DayAdmin)
