from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse

from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login

from .models import Day, Teacher
from .utils import Calendar
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import calendar


def index(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse('hello {}'.format(user.first_name))
        # Redirect to a success page.
    else:
        # Return an 'invalid login' error message.
        return HttpResponse('hello xx')

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
    template_name = 'kg_reservation/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        try:
            teacher = Teacher.objects.get(user=user)
            kg = teacher.kindergarten
        except ObjectDoesNotExist as exp:
            parent = Parent.objects.get(user=user)
            kg = parent.kindergarten

        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(datetime.date.today())

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

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
