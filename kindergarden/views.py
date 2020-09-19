from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
import csv

from .serializers import DaySerializer
from rest_framework.views import APIView
from rest_framework.response import Response

import datetime
import calendar
from django.shortcuts import get_object_or_404
from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from .models import Day, Teacher, Kindergarten, Parent, Child, TeachersDay
from .utils import Calendar
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .utils import plan_month


class MonthView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):

    model = Day

    def test_func(self):
        return is_admin_teacher(self.request.user)

    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(user=self.request.user)
        kindergarten = teacher.kindergarten
        response = HttpResponse(content_type="text/csv")
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        dates = []
        for w in calendar.monthcalendar(year, month):
            for d in w:
                if d > 0:
                    dates.append(d)

        response["Content-Disposition"] = "attachment; filename=\"dochazka_{}-{}.csv\"".format(
            year, month)

        writer = csv.writer(response)
        writer.writerow(["Jméno"] + dates)
        for child in kindergarten.childern:
            present_list = child.present_list(year, month)
            writer.writerow([child.name] + [present_list[d] for d in present_list])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            context['user'] = teacher
        except Exception as e:
            parent = Parent.objects.get(user=self.request.user)
            context['user'] = parent

    def get_queryset(self):
        teacher = Teacher.objects.get(user=self.request.user)
        kindergarten = teacher.kindergarten
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        month_range = calendar.monthrange(year, month)
        return Day.objects.filter(
            kindergarten=kindergarten,
            date__gte=datetime.date(year=year, month=month, day=1),
            date__lte=datetime.date(year=year, month=month, day=month_range[1]),
        )

class ParentView(LoginRequiredMixin, generic.DetailView):

    model = Parent

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['childern'] = Child.objects.filter(parent=self.object)
        context["kindergarten"] = self.object.kindergarten
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            context['user'] = teacher
        except Exception as e:
            parent = Parent.objects.get(user=self.request.user)
            context['user'] = parent
        return context

    def get_object(self, **kwargs):
        if not "pk" in self.kwargs:
            return get_object_or_404(Parent, user=self.request.user)
        else:
            return get_object_or_404(Parent, pk=self.kwargs["pk"])



class TeacherView(LoginRequiredMixin, generic.DetailView):

    model = Teacher
    loging_url = "/login/"
    redirect_field_name = "redirect_to"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['kindergarten'] = self.object.kindergarten

        try:
            teacher = Teacher.objects.get(user=self.request.user)
            context['user'] = teacher
        except Exception as e:
            parent = Parent.objects.get(user=self.request.user)
            context['user'] = parent

        return context

    def get_object(self, **kwargs):
        if not "pk" in self.kwargs:
            return get_object_or_404(Teacher, user=self.request.user)
        else:
            return get_object_or_404(Teacher, pk=self.kwargs["pk"])

def kgview(request, uri_name):
    print(uri_name)

class KindergartenView(generic.DetailView):

    model = Kindergarten
    slug_field = "uri_name"

    def get_object(self):
      object = get_object_or_404(Kindergarten,uri_name=self.kwargs['uri_name'])
      return object

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        if self.request.user and not self.request.user.is_anonymous:
            teachers = Teacher.objects.filter(user=self.request.user)
            parents = Parent.objects.filter(user=self.request.user)
            if teachers.count():
                teacher = teachers[0]
                context["teacher"] = teachers
                context['childern'] = Child.objects.filter(parent__kindergarten=teacher.kindergarten)
                context['teachers'] = Teacher.objects.filter(kindergarten=teacher.kindergarten)
            elif parents.count():
                parent = parents[0]
                context["parent"] = parent
                context['teachers'] = Teacher.objects.filter(kindergarten=parent.kindergarten)
            else:
                pass

        if not self.request.user.is_anonymous:
            teachers = Teacher.objects.filter(user=self.request.user)
            parents = Parent.objects.filter(user=self.request.user)
            if teachers.count():
                context['user'] = teachers[0]
            elif parents.count():
                context['user'] = parent
        else:
            context["user"] = None

        return context

def _get_day_index(day_name):
    days = ["monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday"]

    return days.index(day_name.lower())


class DayOfWeekView(LoginRequiredMixin, APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, year, month, day):
        day = self.get_object(year, month, day)
        serializer = DaySerializer(day, many=False)
        return Response(serializer.data)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        try:
            teacher = Teacher.objects.get(user=self.request.user)
            context['user'] = teacher
        except Exception as e:
            parent = Parent.objects.get(user=self.request.user)
            context['user'] = parent

    def get_object(self, year, month, day_name):
        #day_name = self.kwargs["day"].lower()
        #year = self.kwargs["year"]
        #month = self.kwargs["month"]
        today = datetime.date.today()

        cal = calendar.monthcalendar(year, month)
        for week in cal:
            date_number = week[_get_day_index(day_name)] 
            if date_number > 0 and date_number >= today.day:
                return Day.objects.get(date=datetime.date(year=year, month=month, day=date_number))


class DayView(LoginRequiredMixin, generic.DetailView):

    model = Day

    def get_object(self, **kwargs):

        user = self.request.user
            
        try:
            teacher = Teacher.objects.get(user=user)
            self.kg = teacher.kindergarten
        except ObjectDoesNotExist as exp:
            parent = Parent.objects.get(user=user)
            self.kg = parent.kindergarten

        return get_object_or_404(Day, kindergarten=self.kg,
               date=datetime.date(self.kwargs["year"], self.kwargs["month"], self.kwargs["day"]))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        parents = Parent.objects.filter(user=self.request.user, kindergarten=self.kg)
        if len(parents):
            context["parent"] = self.get_parent_context(parents[0])

        teachers = Teacher.objects.filter(user=self.request.user)
        if len(teachers):
            context["teacher_view"] = self.get_teacher_context(teachers[0])

        context["past"] = False
        now = datetime.datetime.now()
        latest = datetime.datetime(now.year, now.month, now.day, 20, 00)
        day = datetime.datetime(self.object.date.year, self.object.date.month, self.object.date.day)
        if latest > day:
            context["past"] = True

        # Add in a QuerySet of all the books
        #context['childern'] = Child.objects.filter()
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            context['user'] = teacher
        except Exception as e:
            parent = Parent.objects.get(user=self.request.user)
            context['user'] = parent

        return context

    def get_parent_context(self, parent):
        context = {}
        day = self.object
        childern_planned = Child.objects.filter(parent=parent, days__in=[day])
        childern_present = Child.objects.filter(parent=parent, present__in=[day])
        childern_all = Child.objects.filter(parent=parent)
        childern_absent = Child.objects.filter(parent=parent, absent_all__in=[day])
        teachers = Teacher.objects.filter(days_planned=day)
        context["parent"] = parent
        context["teachers_for_the_day"] = teachers
        context["childern_planned"] = [ch.pk for ch in childern_planned]
        context["childern_present"] = [ch.pk for ch in childern_present]
        context["childern_absent"] = [ch.pk for ch in childern_absent]
        context["childern_all"] = childern_all
        return context

    def get_teacher_context(self, teacher):
        context = {}
        day = self.object
        childern_planned = Child.objects.filter(parent__kindergarten=teacher.kindergarten, days__in=[day])
        childern_present = Child.objects.filter(parent__kindergarten=teacher.kindergarten, present__in=[day])
        childern_absent = Child.objects.filter(parent__kindergarten=teacher.kindergarten, absent_all__in=[day])
        childern_all = Child.objects.filter(parent__kindergarten=teacher.kindergarten)
        teachers = Teacher.objects.filter(days_planned=day)
        for t in teachers:
            days = TeachersDay.objects.filter(date=day.date, teacher=teacher)
            if len(days) > 0:
                t.today = days[0]
        context["teacher"] = teacher
        context["teachers_for_the_day"] = teachers
        context["childern_planned"] = [ch.pk for ch in childern_planned]
        context["childern_present"] = [ch.pk for ch in childern_present]
        context["childern_absent"] = [ch.pk for ch in childern_absent]
        context["childern_all"] = childern_all
        context["meals"] = day.meals
        return context





class ChildView(generic.DetailView):

    model = Child
    slug_field = "uuid"
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["parent"] = self.object.parent
        # Add in a QuerySet of all the books
        #context['childern'] = Child.objects.filter()
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            context['user'] = teacher
        except Exception as e:
            parent = Parent.objects.get(user=self.request.user)
            context['user'] = parent
        return context

class KindergartensView(generic.ListView):
    model = Kindergarten
    template_name = 'kindergarden/kindergartens.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_anonymous:
            teachers = Teacher.objects.filter(user=self.request.user)
            parents = Parent.objects.filter(user=self.request.user)
            if teachers.count():
                context['user'] = teachers[0]
            elif parents.count():
                context['user'] = parents[0]
            else:
                context["user"] = None
        return context


# ==================================================================
@login_required
def get_parent(request):
    user = request.user
    
    return get_object_or_404(Parent, user=request.user)

@login_required
def get_teacher(request):
    user = request.user
    
    return get_object_or_404(Teacher, user=request.user)

@method_decorator(login_required, name='dispatch')
class CalendarView(generic.ListView):
    model = Day
    template_name = 'kindergarden/calendar.html'

    def get(self, request, *args, **kwargs):
        if "/calendar/" == request.path:
            today = datetime.date.today()
            year = today.year
            month = today.month
            return HttpResponseRedirect(reverse('month', args=(year,month)))

        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        self.teacher = get_teacher(self.request)
        if self.teacher.is_admin:
            plan_month(self.teacher.kindergarten, self.kwargs["year"],
                    self.kwargs["month"])
            url = reverse("month", args=[self.kwargs["year"], self.kwargs["month"]])
            return HttpResponseRedirect(url)
        else:
            self.get()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        if "year" in self.kwargs:
            year = self.kwargs["year"]
            month = self.kwargs["month"]
        else:
            year = today.year
            month = today.month

        user = self.request.user
        ch_reserved = []
        ch_present = []

        month_filter = {

                "date__year": year,
                "date__month": month
        }
        context["year"] = year
        context["month"] = month
        teacher = None
        parent = None
        try:
            teacher = Teacher.objects.get(user=user)
            kg = teacher.kindergarten
            context["teacher"] = teacher
            context["kindergarten"] = teacher.kindergarten
            context["user"] = teacher
        except ObjectDoesNotExist as exp:
            parent = Parent.objects.get(user=user)
            kg = parent.kindergarten
            context["parent"] = parent
            context["user"] = parent
            ch_reserved = {ch: [d for d in ch.days.filter(**month_filter)] for ch in parent.child_set.all()}
            ch_present = {ch: [d for d in ch.present.filter(**month_filter)] for ch in parent.child_set.all()}
            context["kindergarten"] = parent.kindergarten

        days = Day.objects.filter(kindergarten=kg, **month_filter)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(datetime.date(year=year,
            month=month, day=1))

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(
                teacher=teacher,
                withyear=True,
                days=days,
                childern_present=ch_present,
                childern_reserved=ch_reserved
        )
        context['calendar'] = mark_safe(html_cal)

        time_delta_forward = datetime.timedelta(days=calendar.monthrange(year, month)[1])

        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        time_delta_backward = datetime.timedelta(days=calendar.monthrange(prev_year, prev_month)[1])
        next_month_day = datetime.date(year=year, month=month, day=1) + time_delta_forward

        previous_month_day = datetime.date(year=year, month=month, day=1) - time_delta_backward
        context['previous_month'] = previous_month_day.month
        context['previous_year'] = previous_month_day.year
        context['next_month'] = next_month_day.month
        context['next_year'] = next_month_day.year
        context['this_month'] = today.month
        context['this_year'] = today.year
        context["kindergarden"] = kg
        return context


def is_admin_teacher(user):
    try:
        Teacher.objects.get(user=user)
        return Teacher.is_admin
    except ObjectDoesNotExist as e:
        return False


#@user_passes_test(can_save_day)
@login_required(login_url="login")
def save_day(request, year, month, day):
    day = Day.objects.get(date=datetime.date(year, month, day))
    form = request.POST

    teachers = Teacher.objects.filter(user=request.user)
    parents = Parent.objects.filter(user=request.user)

    if teachers.count():
        kindergarten = teachers[0].kindergarten
    elif parents.count():
        kindergarten = parents[0].kindergarten

    teachers_for_the_day = Teacher.objects.filter(kindergarten=kindergarten, days_planned=day)

    for child in kindergarten.childern:

        if teachers.count() and teachers[0].is_admin or \
            parents.count() and child.parent == parents[0]:

            if "child-{}-present".format(child.pk) in form:
                if not day in child.present.all():
                    child.present.add(day)
            else:
                if day in child.present.all():
                    child.present.remove(day)
                    child.absent_all.add(day)

            if "child-{}-planned".format(child.pk) in form:
                if not day in child.days.all():
                    if day.capacity > day.child_day_planned.count():
                        child.days.add(day)
                    else:
                        from .utils import CapacityFilled
                        raise CapacityFilled(day, child)

                c_key = "child-{}-compensation".format(child.pk)
                if c_key in form and form[c_key] != "":
                    c_year, c_month, c_day = map(lambda x: int(x), form[c_key].split("-"))
                    compensate_date = datetime.date(c_year, c_month, c_day)
                    child.absent_all.remove(Day.objects.get(date=compensate_date, kindergarten=kindergarten))
            else:
                if day in child.days.all():
                    child.days.remove(day)
                    child.absent_all.add(day)

    if not len(parents):
        for teacher in teachers_for_the_day:
            teachers_day = TeachersDay.objects.filter(date=day.date, teacher=teacher)
            t_key = "teacher-{}-present".format(teacher.pk)
            if form[t_key]:
                units  = list((int(v) for v in form[t_key].split(":")))
                if len(units) > 2:
                    hours, minutes, seconds = units
                elif len(units) == 2:
                    hours, minutes = units
                if len(teachers_day) == 0:
                    teachers_day = TeachersDay.objects.create(date=day.date,
                            teacher=teacher, duration=datetime.timedelta(hours=hours,
                            minutes=minutes))
                else:
                    teachers_day = teachers_day[0]
                    teachers_day.duration =  datetime.timedelta(hours=hours,
                            minutes=minutes)
                    teachers_day.save()

        if "meals" in form:
            day.meals = int(form["meals"])
            day.save()

    url = reverse("day", args=[day.date.year, day.date.month, day.date.day])
    return HttpResponseRedirect(url)

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.date.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - datetime.timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + datetime.timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month
