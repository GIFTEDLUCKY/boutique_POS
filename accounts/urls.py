from django.urls import path
from . import views
from django.utils.module_loading import import_string

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),
    path('register/', import_string('accounts.views.register_user'), name='register'),  # Keep this for the registration view
]
