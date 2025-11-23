from django.urls import path
from . import views
from .views import continue_project

app_name = 'dashboard'  # Add an app name to namespace the URLs

urlpatterns = [
    path('', views.index, name='index'),  # Add the index page URL

    path('continue_project/', continue_project, name='continue_project'),

    path("keepalive/", views.keepalive, name="keepalive"),
]
