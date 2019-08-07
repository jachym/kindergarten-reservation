from django.conf.urls import url
from . import views
from django.urls import path, include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^/$', views.kindergarten, name='kindergarten'),
    url(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),
    #url(r'^/{}/child/{}$', views.index, name='child'),
    #url(r'^/{}/parent/{}$', views.index, name='child'),
    #url(r'^/{}/cal$', views.index, name='calendar'),
    #url(r'^/{}/teacher/day/{}$', views.index, name='day'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name='profile')
]
