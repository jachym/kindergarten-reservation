from django.conf.urls import url
from . import views
from django.urls import path, include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('parent/', views.ParentView.as_view(), name="parent"),
    path('parent/<int:pk>', views.ParentView.as_view(), name="parent"),
    path('teacher/<int:pk>', views.TeacherView.as_view(), name="teacher"),
    #path('kindergarten/<slug:uri_name>/', views.kgview),
    path('<slug:kg>/', views.KindergartenView.as_view(), name="kindergarden"),
    path('<int:year>/<int:month>/', views.CalendarView.as_view(), name="month"),
    path('<int:year>/<int:month>/<int:day>/', views.DayView.as_view(), name="day"),
    path('<int:year>/<int:month>/<int:day>/save', views.save_day, name="day-save"),
    path('child/<uuid:uuid>/', views.ChildView.as_view(), name="child"),
]
