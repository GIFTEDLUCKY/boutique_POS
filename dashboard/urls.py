from django.urls import path
from . import views

app_name = 'dashboard'  # Add an app name to namespace the URLs

urlpatterns = [
    path('', views.index, name='index'),  # Add the index page URL
]
