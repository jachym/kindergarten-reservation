from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

# Create your models here.

class Kindergarten(models.Model):

    uri_name = models.CharField(
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

    note = models.TextField(blank=True)



    def __str__(self):
        return self.name



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kindergarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)
    phone = models.CharField( max_length=20,)

    days = models.ManyToManyField("Day")

    @property
    def name(self):
        if self.user.first_name:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        else:
            return self.user.name

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kindergarten = models.ForeignKey("Kindergarten",
                                    on_delete=models.CASCADE)
    phone = models.CharField( max_length=20,)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

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

    days = models.ManyToManyField("Day")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

class Day(models.Model):

    capacity = models.IntegerField(blank=True, null=True)
    date = models.DateField()
    note = models.TextField(blank=True)
    kindergarten = models.ForeignKey(
        "Kindergarten", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.capacity:
            self.capacity = self.kindergarten.default_capacity

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.date)
