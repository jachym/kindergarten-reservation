from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Day
from django.urls import reverse

class Calendar(HTMLCalendar):
    def __init__(self, date):
        self.year = date.year
        self.month = date.month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, teacher, md, days, teacher_present=[],
            teacher_service=[], childern_present={}, childern_reserved={}):
        this_day = days.filter(date__year=self.year, date__month=self.month, date__day=md)
        d = ''
        day = None
        today = datetime.today().date()

        if len(this_day):
            day = this_day[0]
            if teacher:
                d += f'<div class="capacity"><b>Kapacita:</b> {day.capacity}</div>'
                d += f'<div class="capacity"><b>Počet přihlášených:</b> {childern_reserved} </div>'

            d += '<ul>'
            if day in teacher_service:
                d += f"<li class=\"teacher-service\">Služba</li>"
            if day in teacher_present:
                d += f"<li class=\"teacher-present\">V práci</li>"

            if day.date >= today:
                for child in childern_reserved:
                    child_url = reverse("child", args=[child.uuid])
                    if day in childern_reserved[child]:
                        d += f"<li class=\"child-reserved\"><a href=\"{child_url}\" title=\"rezervováno\">{child}</a></li>"
            else:
                for child in childern_present:
                    child_url = reverse("child", args=[child.uuid])
                    if day in childern_present[child]:
                        d += f"<li class=\"child-present\"><a href=\"{child_url}\" title=\"přítomno\">{child}</a></li>"
                    else:
                        d += f"<li class=\"child-absent\"><a href=\"{child_url}\" title=\"chybělo\">{child}</a></li>"
            d += '</ul>'
            url = reverse("day", args=[self.year, self.month, day.date.day])
            return f"<td class=\"calendar-day\"><div class='date'><a href=\"{url}\">{md}</a></div>{d}</td>"

        elif md != 0:
            return f"<td class=\"calendar-day\"><div class='date'>{md}</div>{d}</td>"
        else:
            return '<td></td>'

    # formats a week as a tr 
    def formatweek(self, teacher, theweek, days, teacher_present, teacher_service,
            childern_present, childern_reserved):
        week = ''
        for d, day in theweek:
            week += self.formatday(teacher, d, days, teacher_present, teacher_service, childern_present, childern_reserved)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, teacher, withyear=True, days=[], teacher_present=[],
            teacher_service=[], childern_present={}, childern_reserved={}):

        #days = Day.objects.filter(date__year=self.year, date__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="table">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(teacher, week, days, teacher_present, teacher_service, childern_present, childern_reserved)}\n'
        return cal
