from django.forms import ModelForm, Textarea
from .models import Child
from django.forms.widgets import CheckboxInput
import datetime
import calendar

class ChildAdminForm(ModelForm):
        class Meta:
            model = Child
            fields = [
                "first_name",
                "last_name",
                "middle_name",
                "uuid",
                "parent",
                "diet",
                "notes",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
            ]

