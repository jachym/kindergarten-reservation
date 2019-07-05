from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

# Create your models here.

class Kindergarten(models.Model):

    name = models.CharField(
        max_length=50,
        help_text=_("The name of the Kindergarten")
    )

    address = models.TextField(
        help_text=_("Precise address")
    )

    phone = models.CharField(
       max_length=20,
    )

    email = models.EmailField()

    web = models.URLField()

    note = models.TextField(blank=True)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kindergarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kindergarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)

class Child(models.Model):

    first_name = models.CharField(
        max_length=20)

    last_name = models.CharField(
        max_length=20)

    middle_name = models.CharField(
        max_length=50,
        blank=True
    )

    kindegarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)
    parent = models.ForeignKey("Parent",
                                    on_delete=models.PROTECT)

class Day(models.Model):

    capacity = models.IntegerField()
    date = models.DateField()
    note = models.TextField(blank=True)

    children = models.ManyToManyField("Child")
    teachers = models.ManyToManyField("Teacher")
