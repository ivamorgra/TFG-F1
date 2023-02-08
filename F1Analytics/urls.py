"""F1Analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
#from DataAnalytics.views import get_list
from DataAnalytics import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('index.html/', views.index),
    path('populate/', views.load_data),
    path('loadData/',views.load_dataframes),
    path('drivers/',views.list_drivers),
    path('driver/<int:id>',views.get_driver),
    path('constructors/',views.get_constructors),
    path('constructors/<int:id>',views.get_constructor),
    path('circuits/',views.list_circuits),
    path('circuits/<int:id>',views.get_circuit),
    path('races/',views.list_races),
    path('races/<int:id>', views.details_race),
    path('api/get_followers',views.get_twitter_stats),
    #path('circuitos/',get_list, name='circuits.html'),
]
