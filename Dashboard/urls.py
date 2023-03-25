from django.contrib import admin
from django.urls import path
from Dashboard import views as dashboard_views

urlpatterns = [
    path('',dashboard_views.get_dashboard,name='dashboard'),
    path('twitter/<int:num>',dashboard_views.get_twitter_stats,name='twitter'),
    path('stats/',dashboard_views.get_stats,name='stats'),
    path('standings/',dashboard_views.get_view_standings,name='standings')
]


