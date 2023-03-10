from django.contrib import admin
from django.urls import path, include
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
    path('dashboard/', include('Dashboard.urls')),
]
