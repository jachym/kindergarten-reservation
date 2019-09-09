from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import resolve

from .models import Kindergarten, Teacher, Parent, Day, Child

class ChildKindergartenListFilter(admin.SimpleListFilter):
    title = _('Kindergarten')
    parameter_name = "kindergarten"

    def lookups(self, request, model_admin):
        data  = []
        for k in  Kindergarten.objects.all():
            data.append((k.id, k.name))
        return data

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parent__kindergarten__id=self.value())
        else:
            return queryset


class ChildDaysInline(admin.TabularInline):
    model = Child.days.through
    extra = 0
    verbose_name = _("Reserved day")

class ChildPresentInline(admin.TabularInline):
    model = Child.present.through
    extra = 0
    verbose_name = _("Present day")

class TeacherDaysInline(admin.TabularInline):
    model = Teacher.days.through
    extra = 0
    verbose_name = _("Planned day")

class TeacherPresentInline(admin.TabularInline):
    model = Teacher.present.through
    extra = 0
    verbose_name = _("Present day")

class KindergartenAdmin(admin.ModelAdmin):
    list_display = (
        "name", "phone", "email", "web")

class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "name", "kindergarten", "email", "phone")

    list_filer = ("kindergarten")
    exclude = ("days", "present")

    inlines = [
            TeacherDaysInline, TeacherPresentInline
    ]

    def name(self, teacher):
        return teacher.name

    def email(self, teacher):
        return teacher.user.email

    def child(self, teacher):
        return "ahoj"

class ParentAdmin(admin.ModelAdmin):
    list_display = (
        "name", "kindergarten", "email", "phone", "child")
    list_filter = ("kindergarten", )

    def name(self, parent):
        return str(parent)

    def email(self, parent):
        return parent.user.email

    def child(self, parent):
        return "ahoj"

class ChildAdmin(admin.ModelAdmin):
    list_filter = (ChildKindergartenListFilter, )
    list_display = ("name", "kindergarten", "parent")

    inlines = [
            ChildDaysInline, ChildPresentInline
    ]
    exclude = ("days", "present")

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
    list_display = ("date", "capacity", "kindergarten", "childern_planned",
                    "childern_present", "teachers_planned", "teachers_present")
    list_filter = ("kindergarten",)

    def childern_planned(self, day):
        return day.child_day_planned.count()

    def childern_present(self, day):
        return day.child_day_present.count()

    def teachers_planned(self, day):
        return day.teacher_day_planned.count()

    def teachers_present(self, day):
        return day.teacher_day_present.count()

admin.site.register(Kindergarten, KindergartenAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Day, DayAdmin)
