from django.contrib import admin

from .models import Kindergarten, Teacher, Parent, Day, Child

class KindergartenAdmin(admin.ModelAdmin):
    list_display = (
        "name", "phone", "email", "web")

class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "name", "kindergarten", "email", "phone")

    list_filer = ("kindergarten")

    def name(self, teacher):
        return teacher.name

    def email(self, teacher):
        return teacher.user.email

    def child(self, teacher):
        return "ahoj"

class ParentAdmin(admin.ModelAdmin):
    list_display = (
        "name", "kindergarten", "email", "phone", "child")
    list_filer = ("kindergarten")

    def name(self, parent):
        return self.name

    def email(self, parent):
        return parent.user.email

    def child(self, parent):
        return "ahoj"

class ChildAdmin(admin.ModelAdmin):
    list_filer = ("kindergarten")

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
    list_display = ("date", "capacity", "kindergarten")
    list_filter = ("kindergarten",)

admin.site.register(Kindergarten, KindergartenAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Day, DayAdmin)
