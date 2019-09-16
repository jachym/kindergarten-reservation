from rest_framework import serializers
from .models import Day, Child
import calendar

class DaySerializer(serializers.ModelSerializer):
    day_reservations = serializers.SerializerMethodField()
    day_of_week = serializers.SerializerMethodField()

    class Meta:
        model = Day
        fields = ['date', 'kindergarten', 'capacity', 'note', "program",
        "day_reservations", "day_of_week"]

    def get_day_reservations(self, obj):
        return obj.child_day_planned.count()

    def get_day_of_week(self, obj):

        didx = calendar.weekday(obj.date.year, obj.date.month, obj.date.day)
        return ["monday", "tuesday", "wednesday", "thursday", "friday"][didx]

