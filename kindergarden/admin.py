from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import resolve

from .models import Kindergarten, Teacher, Parent, Day, Child, TeachersDay
from .forms import ChildAdminForm

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

class ChildAbsentInline(admin.TabularInline):
    model = Child.absent_all.through
    extra = 0
    verbose_name = _("Absent day")

class KindergartenAdmin(admin.ModelAdmin):
    list_display = (
        "name", "phone", "email", "web")

class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "name", "kindergarten", "email", "phone", "this_month", "last_month")

    list_filer = ("kindergarten")
    exclude = ("days_planned", "days_present")

    fieldsets = (
            (None, {"fields": ("user", "kindergarten", "is_admin")}),
            ("Contact", {"fields": ("phone",)}),
            ("Planning", {"fields": ("monday", "tuesday", "wednesday",
            "thursday", "friday")}),

    )

    def name(self, teacher):
        return teacher.name

    def email(self, teacher):
        return teacher.user.email


class ParentAdmin(admin.ModelAdmin):
    list_display = (
        "name", "kindergarten", "email", "phone", "childs")
    list_filter = ("kindergarten", )

    def name(self, parent):
        return str(parent)

    def email(self, parent):
        return parent.user.email

    def childs(self, parent):
        return " <br /> ".join([ch.name for ch in Child.objects.filter(parent=parent)])

class ChildAdmin(admin.ModelAdmin):
    list_filter = (ChildKindergartenListFilter, )
    list_display = ("name", "kindergarten", "parent")

    inlines = [
            ChildDaysInline, ChildPresentInline, ChildAbsentInline
    ]
    exclude = ("days", "present")

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['form'] = ChildAdminForm
        return super().get_form(request, obj, **kwargs)

class ChildInline(admin.TabularInline):
    model = Child.days.through
    extra = 0

class DayAdmin(admin.ModelAdmin):
    inlines = [
            ChildInline
    ]
    exclude = ("days", "teachers")
    list_display = ("date", "capacity", "kindergarten", "childern_planned",
                    "childern_present", "meals")
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
