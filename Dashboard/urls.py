from django.contrib import admin
from django.urls import path
from Dashboard import views as dashboard_views

urlpatterns = [
    path('',dashboard_views.get_dashboard,name='dashboard'),
    path('dashboard/loading',dashboard_views.get_loader,name='loader'),
    #path('twitter/<int:num>',dashboard_views.get_twitter_stats,name='twitter'),
    path('stats/',dashboard_views.get_stats,name='stats'),
    path('meteo',dashboard_views.get_view_weather,name='meteo'),
    path('standings/',dashboard_views.get_view_standings,name='standings')
]


