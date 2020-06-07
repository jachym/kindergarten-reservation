from datetime import datetime, timedelta, date as mydate
from calendar import HTMLCalendar
from calendar import monthcalendar
from .models import Day
from django.urls import reverse

from .models import Child
from .models import Parent

class CapacityFilled(Exception):
    def __init__(self, child, day):
        self.day = day
        self.child = child
        super(CapacityFilled, self).__init__("Capacity of {} for day {} filled with child {}".format(day.capacity, day.date, child))

class Calendar(HTMLCalendar):
    def __init__(self, date):
        self.year = date.year
        self.month = date.month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, teacher, md, days, childern_present={}, childern_reserved={}):
        this_day = days.filter(date__year=self.year, date__month=self.month, date__day=md)
        d = ''
        day = None
        today = datetime.today().date()

        if len(this_day):
            day = this_day[0]
            if teacher:
                ch_planned = len(day.child_day_planned.all())
                d += f'{ch_planned}/{day.capacity}'
                if day.date < today:
                    ch_present = len(day.child_day_present.all())
                    d += f'<br /><strong>{ch_present}</strong>'

            if day.date >= today:
                for child in childern_reserved:
                    child_url = reverse("child", args=[child.uuid])
                    if day in childern_reserved[child]:
                        d += f"<a role=\"button\" class=\"btn btn-primary btn-sm \" href=\"{child_url}\" title=\"rezervováno\">{child}</a>"
                    else:
                        d += "&nbsp;"
            else:
                for child in childern_present:
                    child_url = reverse("child", args=[child.uuid])
                    if day in childern_present[child]:
                        d += f"<a role=\"button\" class=\"btn btn-success btn-sm \" href=\"{child_url}\" title=\"přítomno\">{child}</a>"
                    elif day in childern_reserved[child]:
                        d += f"<a role=\"button\" class=\"btn btn-danger btn-sm \" href=\"{child_url}\" title=\"chybělo\">{child}</a>"
                    else:
                        d += "<div>&nbsp;</div>"

            url = reverse("day", args=[self.year, self.month, day.date.day])

            d = f'''
              <div class="card">
                <div class="card-header"><a style="width:100%" href=\"{url}\">{md}</a></div>
                <div class="card-body">{d}</div>
              </div>
            '''

            if day.date == today:
                return f"<td class=\"calendar-day today text-center\">{d}</td>"
            else:
                return f"<td class=\"calendar-day text-center\">{d}</td>"

        elif md != 0:
            d = f'''
              <div class="card">
                <div class="card-header">{md}</div>
                <div class="card-body">{d}</div>
              </div>
            '''
            if day == today:
                return f"<td class=\"calendar-day today text-center\">{d}</td>"
            else:
                return f"<td class=\"calendar-day text-center\">{d}</td>"
        else:
            return '<td>&nbsp;</td>'

    # formats a week as a tr 
    def formatweek(self, teacher, theweek, days, childern_present, childern_reserved):
        week = ''
        for d, day in theweek:
            week += self.formatday(teacher, d, days, childern_present, childern_reserved)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, teacher, withyear=True, days=[], childern_present={}, childern_reserved={}):

        #days = Day.objects.filter(date__year=self.year, date__month=self.month)

        cal = f'<div class="table-responsive"><table border="0" cellpadding="0" cellspacing="0" class="table table-sm">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(teacher, week, days, childern_present, childern_reserved)}\n'
        cal += "</table></div>"
        return cal


def plan_month(kindergarten, year, month):
    today = datetime.today().date()

    childern = []
    for par in Parent.objects.filter(kindergarten=kindergarten):
        for child in par.child_set.all():
            childern.append(child)

    days = monthcalendar(year, month)
    for week in days:
        for dayidx in list(range(len(week))):
            if week[dayidx] == 0:
                continue
            if dayidx > 4:
                continue

            date = mydate(year=year, month=month, day=week[dayidx])

            if date > today:

                mydays = kindergarten.day_set.filter(date=date)

                if len(mydays) == 0:
                    day = Day(date=date, kindergarten=kindergarten)
                    day.save()
                else:
                    day = mydays[0]

                # BOŽE !!! omlouvám se svému budoucímu já za tuhle hrůzu
                for child in childern:
                    if dayidx == 0:
                        if child.monday and not child.days.filter(date=day.date):
                            if day.child_day_planned.count() >= day.capacity:
                                raise CapacityFilled(child, day)
                            else:
                                child.days.add(day)
                        elif not child.monday:
                            child.days.remove(day)
                    if dayidx == 1:
                        if child.tuesday and not child.days.filter(date=day.date):
                            if day.child_day_planned.count() >= day.capacity:
                                raise CapacityFilled(child, day)
                            else:
                                child.days.add(day)
                        elif not child.tuesday:
                            child.days.remove(day)
                    if dayidx == 2:
                        if child.wednesday and not child.days.filter(date=day.date):
                            if day.child_day_planned.count() >= day.capacity:
                                raise CapacityFilled(child, day)
                            else:
                                    child.days.add(day)
                        elif not child.wednesday:
                            child.days.remove(day)
                    if dayidx == 3:
                        if child.thursday and not child.days.filter(date=day.date):
                            if day.child_day_planned.count() >= day.capacity:
                                raise CapacityFilled(child, day)
                            else:
                                child.days.add(day)
                        elif not child.thursday:
                            child.days.remove(day)
                    if dayidx == 4:
                        if child.friday and not child.days.filter(date=day.date):
                            if day.child_day_planned.count() >= day.capacity:
                                raise CapacityFilled(child, day)
                            else:
                                child.days.add(day)
                        elif not child.friday:
                            child.days.remove(day)

