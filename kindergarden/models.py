from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import gettext as _
from datetime import datetime, timedelta, date as mydate
import calendar
from django.db.models import Subquery

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import uuid
import datetime
from calendar import monthrange


# Create your models here.

class Kindergarten(models.Model):

    uri_name = models.SlugField(
        unique=True,
        max_length=24,
        help_text=_("URL identifier")
    )

    name = models.CharField(
        max_length=50,
        help_text=_("The name of the Kindergarten")
    )

    #ico = models.IntegerField(
    #    blank=True
    #)

    address = models.TextField(
        help_text=_("Precise address")
    )

    phone = models.CharField(
       max_length=20,
    )

    email = models.EmailField()

    web = models.URLField()

    default_capacity = models.IntegerField(blank=True, null=True)

    compensation_length = models.IntegerField(
        default=3,
        help_text=_("Number of months where parent can compensate missing days")
    )

    note = models.TextField(blank=True)

    def save(self, *args, **kwargs):

        label = Kindergarten._meta.app_label
        content_type = ContentType.objects.get_for_model(Kindergarten)
        codename = '{}_edit_{}'.format(label, self.uri_name)
        name = 'Can edit Kindergarten {}'.format(self.name)
        group_name = '{}_{}'.format(label, self.uri_name)

        new_perm, created = Permission.objects.get_or_create(
            codename=codename, name=name, content_type=content_type)

        new_group, created = Group.objects.get_or_create(name=group_name)

        new_group.permissions.add(new_perm)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def childern(self):
        return Child.objects.filter(parent__kindergarten=self)



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kindergarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)
    phone = models.CharField( max_length=20,)

    #days = models.ManyToManyField("Day", blank=True, related_name="teacher_day_planned")
    #present = models.ManyToManyField("Day", blank=True, related_name="teacher_day_present")
    is_admin = models.BooleanField(blank=True, default=False)

    monday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"monday-check\"></div>")
    tuesday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"tuesday-check\"></div>")
    wednesday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"wednesday-check\"></div>")
    thursday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"thursday-check\"></div>")
    friday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"friday-check\"></div>")

    days_planned = models.ManyToManyField("Day", blank=True, related_name="teacher_day_planned")

    @property
    def name(self):
        if self.user.first_name:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    @property
    def type(self):
        return "teacher"

    def save(self, *args, **kwargs):
        from .utils import plan_month # this is here due to circular import

        label = Teacher._meta.app_label
        group_name = '{}_{}'.format(label, self.kindergarten.uri_name)

        group = Group.objects.get(name=group_name)
        group.user_set.add(self.user)


        super().save(*args, **kwargs)

        # plan this month and next month automatically
        today = datetime.today()
        plan_month(self.kindergarten, today.year, today.month)

        if today.month == 12:
            month = 1
            year = today.year + 1
        else:
            month = today.month + 1
            year = today.year

        plan_month(self.kindergarten, year, month)

        super().save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    @property
    def this_month(self):

        today = datetime.date.today()
        year = today.year
        month = today.month
        min_date = datetime.date(year, month, 1)
        max_date = datetime.date(year, month, monthrange(year, month)[1])

        days = TeachersDay.objects.filter(date__gte=min_date, date__lte=max_date,
                teacher=self)

        return sum([d.duration.total_seconds()/3600 for d in days])

    @property
    def last_month(self):

        today = datetime.date.today()
        year = today.year
        month = today.month

        month = month - 1
        if month < 1:
            month = 12
            year = year -1
        min_date = datetime.date(year, month, 1)
        max_date = datetime.date(year, month, monthrange(year, month)[1])

        days = TeachersDay.objects.filter(date__gte=min_date, date__lte=max_date,
                teacher=self)

        return sum([d.duration.total_seconds()/3600 for d in days])

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kindergarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)
    phone = models.CharField( max_length=20,)


    def __str__(self):
        if self.user.first_name:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    @property
    def type(self):
        return "parent"

class Child(models.Model):

    first_name = models.CharField(
        max_length=20)

    last_name = models.CharField(
        max_length=20)

    middle_name = models.CharField(
        max_length=50,
        blank=True
    )

    uuid = models.UUIDField(default=uuid.uuid4)

    parent = models.ForeignKey("Parent", on_delete=models.PROTECT)

    diet = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    monday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"monday-check\"></div>")
    tuesday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"tuesday-check\"></div>")
    wednesday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"wednesday-check\"></div>")
    thursday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"thursday-check\"></div>")
    friday = models.BooleanField(blank=False, default=False,
            help_text="<div id=\"friday-check\"></div>")

    days = models.ManyToManyField("Day", blank=True, related_name="child_day_planned")
    present = models.ManyToManyField("Day", blank=True, related_name="child_day_present")
    absent_all = models.ManyToManyField("Day", blank=True, related_name="child_day_absent")

    @property
    def kindergarten(self):
        return self.parent.kindergarten


    def present_list(self, year, month):

        mylist = {}

        for week in calendar.monthcalendar(year, month):
            for day_nr in week:
                if day_nr == 0:
                    continue
                date = mydate(year, month, day_nr)

                reserved = self.days.filter(date=date).count() == 1
                present = self.present.filter(date=date).count() == 1
                if reserved and present:
                    mylist[date] = True
                elif reserved and not present:
                    mylist[date] = False
                elif not reserved and not present:
                    mylist[date] = None

        return mylist



    @property
    def absent(self):

        today = datetime.today()
        year = today.year
        if today.month < 9:
            year = year - 1

        start = mydate(year=year, month=9, day=1)
        return self.absent_all.filter(date__gte=start).exclude(
            date__in=[d.date for d in self.present.all()]
        )

        return self.days.filter(date__gte=start,
                date__lt=today).exclude(
            date__in=[d.date for d in self.present.all()]
        )

    @property
    def first_compensation(self):
        return self.compensation()[0]

    def compensation(self, today=None):
        months = self.kindergarten.compensation_length
        if today is None:
            today = datetime.today()

        month = today.month - months
        year = today.year
        if month < 1:
            month = 12 + today.month - months
            year = today.year - 1

        day = today.day
        if calendar.monthrange(year, month)[1] < today.day:
            day = calendar.monthrange(year, month)[1]

        last_date = mydate(year=year, month=month, day=day)

        days_compensate = self.absent.filter(date__gte=last_date)
        return days_compensate

    def save(self, *args, **kwargs):
        from .utils import plan_month # this is here due to circular import

        super().save(*args, **kwargs)

        # plan this month and next month automatically
        today = datetime.today()
        plan_month(self.kindergarten, today.year, today.month)

        if today.month == 12:
            month = 1
            year = today.year + 1
        else:
            month = today.month + 1
            year = today.year

        plan_month(self.kindergarten, year, month)

    @property
    def name(self):
        return str(self)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Day(models.Model):

    date = models.DateField()
    capacity = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True)
    program = models.TextField(blank=True)
    meals = models.IntegerField(default=0)
    kindergarten = models.ForeignKey(
        "Kindergarten", on_delete=models.CASCADE)

    teachers = models.ManyToManyField(Teacher)

    def save(self, *args, **kwargs):

        if self.capacity is None:
            self.capacity = self.kindergarten.default_capacity

        #if len(Day.objects.all().filter(date=self.date,
        #                          kindergarten=self.kindergarten)) >  0:
        #    raise Exception("Date already exists")


        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.date)

class TeachersDay(models.Model):
    date = models.DateField()
    duration = models.DurationField()
    note = models.TextField(blank=True)
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date)

    @property
    def time(self):
        hours = int(self.duration.total_seconds()/3600)
        minutes = (self.duration.total_seconds()%3600)/60
        return "{h:02d}:{m:02d}:00".format(h=hours, m=int(minutes))


