from django.conf.urls import url
from . import views
from django.urls import path, include
from rest_framework import routers

from photologue.sitemaps import GallerySitemap, PhotoSitemap


urlpatterns = [
    url(r'^$', views.KindergartensView.as_view(), name='index'),
    path('parent/', views.ParentView.as_view(), name="parent"),
    path('teacher/', views.TeacherView.as_view(), name="teacher"),
    path('parents/<int:pk>/', views.ParentView.as_view(), name="parent"),
    path('teachers/<int:pk>/', views.TeacherView.as_view(), name="teacher_by_id"),
    path('calendar/', views.CalendarView.as_view(), name="calendar"),
    path('<slug:uri_name>/', views.KindergartenView.as_view(), name="kindergarden"),
    path('<int:year>/<int:month>/', views.CalendarView.as_view(), name="month"),
    path('<int:year>/<int:month>/report/', views.MonthView.as_view(), name="month_report"),
    path('<int:year>/<int:month>/<int:day>/', views.DayView.as_view(), name="day"),
    path('<int:year>/<int:month>/<int:day>/save/', views.save_day, name="day-save"),
    path('child/<uuid:uuid>/', views.ChildView.as_view(), name="child"),
    path('dayofweek/<int:year>/<int:month>/<str:day>/', views.DayOfWeekView.as_view(), name="day-of-week"),
]
