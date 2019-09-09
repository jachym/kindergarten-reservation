from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from datetime import datetime
import calendar
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login

from .models import Day, Teacher, Kindergarten, Parent, Child
from .utils import Calendar
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import calendar

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class ParentView(LoginRequiredMixin, generic.DetailView):

    model = Parent
    #model = User
    #context_object_name = 'foo'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['childern'] = Child.objects.filter(parent=self.object)
        return context


class TeacherView(LoginRequiredMixin, generic.DetailView):

    model = Teacher
    loging_url = "/login/"
    redirect_field_name = "redirect_to"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['kindergarten'] = self.object.kindergarten
        return context

def kgview(request, uri_name):
    print(uri_name)

class KindergartenView(generic.DetailView):

    model = Kindergarten
    slug_field = "uri_name"
    slug_url_kwarg = 'kg'

    def xxxget_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        #context['childern'] = Child.objects.filter()
        return context


class DayView(LoginRequiredMixin, generic.DetailView):

    model = Day

    def get_object(self, **kwargs):

        user = self.request.user
        try:
            teacher = Teacher.objects.get(user=user)
            kg = teacher.kindergarten
        except ObjectDoesNotExist as exp:
            parent = Parent.objects.get(user=user)
            kg = parent.kindergarten

        return get_object_or_404(Day, kindergarten=kg,
               date=datetime.date(self.kwargs["year"], self.kwargs["month"], self.kwargs["day"]))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        parents = Parent.objects.filter(user=self.request.user)
        if len(parents):
            context["parent"] = self.get_parent_context(parents[0])

        teachers = Teacher.objects.filter(user=self.request.user)
        if len(teachers):
            context["teacher"] = self.get_teacher_context(teachers[0])

        # Add in a QuerySet of all the books
        #context['childern'] = Child.objects.filter()
        return context

    def get_parent_context(self, parent):
        context = {}
        day = self.object
        childern_planned = Child.objects.filter(parent=parent, days__in=[day])
        childern_present = Child.objects.filter(parent=parent, present__in=[day])
        childern_all = Child.objects.filter(parent=parent)
        context["parent"] = parent
        context["childern_planned"] = [ch.pk for ch in childern_planned]
        context["childern_present"] = [ch.pk for ch in childern_present]
        context["childern_all"] = childern_all
        return context

    def get_teacher_context(self, teacher):
        context = {}
        day = self.object
        childern_planned = Child.objects.filter(parent__kindergarten=teacher.kindergarten, days__in=[day])
        childern_present = Child.objects.filter(parent__kindergarten=teacher.kindergarten, present__in=[day])
        childern_all = Child.objects.filter(parent__kindergarten=teacher.kindergarten)
        context["teacher"] = teacher
        context["childern_planned"] = [ch.pk for ch in childern_planned]
        context["childern_present"] = [ch.pk for ch in childern_present]
        context["childern_all"] = childern_all
        context["planned"] = day in teacher.days.all()
        context["present"] = day in teacher.present.all()
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
        print(self.object.parent)
        return context

@login_required
def index(request):

    user = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
    elif request.user:
        user = request.user

    if user is not None:
        login(request, user)
        return HttpResponse('hello {}'.format(user.first_name))
        # Redirect to a success page.
    else:
        # Return an 'invalid login' error message.
        return HttpResponse('hello xx')


# ==================================================================
@login_required
def get_parent(request):
    user = request.user
    
    return get_object_or_404(Parent, user=request.user)

@login_required
def get_teacher(request):
    user = request.user
    
    return get_object_or_404(Teacher, user=request.user)

@login_required
def profile(request):
    user = request.user
    
    try:
        teacher = Teacher.objects.get(user=user)
        return _teacher_profile(teacher, request)
    except ObjectDoesNotExist as exp:
        parent = Parent.objects.get(user=user)
        return _teacher_profile(parent, request)


def _teacher_profile(teacher, request):
        return HttpResponse('hello teacher')


def _parent_profile(teacher, request):
        return HttpResponse('hello parent')


@method_decorator(login_required, name='dispatch')
class CalendarView(generic.ListView):
    model = Day
    template_name = 'kindergarden/calendar.html'

    def post(self, request, *args, **kwargs):
        self.teacher = get_teacher(self.request)
        if self.teacher.is_admin:
            self.plan_month()
            url = reverse("month", args=[self.kwargs["year"], self.kwargs["month"]])
            return HttpResponseRedirect(url)
        else:
            self.get()

    def plan_month(self):

        kindergarten = self.teacher.kindergarten

        childern = []
        for par in Parent.objects.filter(kindergarten=kindergarten):
            for child in par.child_set.all():
                childern.append(child)

        days = calendar.monthcalendar(self.kwargs["year"], self.kwargs["month"])
        for week in days:
            for dayidx in list(range(len(week)-1)):
                if week[dayidx] == 0:
                    continue
                if dayidx > 4:
                    continue

                date = datetime.date(year=self.kwargs["year"], month=self.kwargs["month"], day=week[dayidx])
                mydays = kindergarten.day_set.filter(date=date)

                if len(mydays) == 0:
                    day = Day(date=date, kindergarten=kindergarten)
                    day.save()
                else:
                    day = mydays[0]


                for child in childern:
                    if dayidx == 0 and child.monday and not child.days.filter(date=day.date):
                        child.days.add(day)
                    if dayidx == 1 and child.thuesday and not child.days.filter(date=day.date):
                        child.days.add(day)
                    if dayidx == 2 and child.wednesday and not child.days.filter(date=day.date):
                        child.days.add(day)
                    if dayidx == 3 and child.thursday and not child.days.filter(date=day.date):
                        child.days.add(day)
                    if dayidx == 4 and child.friday and not child.days.filter(date=day.date):
                        child.days.add(day)
                    child.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        t_present = []
        t_days = []
        ch_reserved = []
        ch_present = []
        teacher = False

        month_filter = {

                "date__year": self.kwargs["year"],
                "date__month": self.kwargs["month"]
        }
        try:
            teacher = Teacher.objects.get(user=user)
            kg = teacher.kindergarten
            context["teacher"] = teacher
            t_days = teacher.days.filter(**month_filter)
            t_present = teacher.present.filter(**month_filter)
        except ObjectDoesNotExist as exp:
            parent = Parent.objects.get(user=user)
            kg = parent.kindergarten
            context["parent"] = parent
            ch_reserved = {ch: [d for d in ch.days.filter(**month_filter)] for ch in parent.child_set.all()}
            ch_present = {ch: [d for d in ch.present.filter(**month_filter)] for ch in parent.child_set.all()}

        days = Day.objects.filter(kindergarten=kg, **month_filter)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(datetime.date(year=self.kwargs["year"],
            month=self.kwargs["month"], day=1))

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(
                teacher=teacher,
                withyear=True,
                days=days,
                teacher_present=t_present,
                teacher_service=t_days,
                childern_present=ch_present,
                childern_reserved=ch_reserved
        )
        context['calendar'] = mark_safe(html_cal)
        d = get_date(self.request.GET.get('month', None))
        this_day = datetime.datetime.today().date()
        time_delta_forward = datetime.timedelta(days=calendar.monthrange(self.kwargs["year"], self.kwargs["month"])[1])
        month = self.kwargs["month"] - 1
        year = self.kwargs["year"]
        if month == 0:
            year -= 1
            month = 12

        time_delta_backward = datetime.timedelta(days=calendar.monthrange(year, month)[1])
        next_month_day = datetime.date(year=self.kwargs["year"], month=self.kwargs["month"], day=1) + time_delta_forward
        previous_month_day = datetime.date(year=self.kwargs["year"], month=self.kwargs["month"], day=1) - time_delta_backward
        context['previous_month'] = previous_month_day.month
        context['previous_year'] = previous_month_day.year
        context['next_month'] = next_month_day.month
        context['next_year'] = next_month_day.year
        context['this_month'] = this_day.month
        context['this_year'] = this_day.year
        context["kindergarden"] = kg
        return context

def save_day(request, kindergarten, day):
    pass

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
