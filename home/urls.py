from django.urls import path
from .views import *

urlpatterns = [
    # pages
    path('', homepage, name='homepage'),
    url('loginPage$', loginPage, name='loginPage'),
    url('logout$', user_logout, name='logout'),

    ]