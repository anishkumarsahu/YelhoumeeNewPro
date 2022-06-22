from django.urls import path
from .views import *

urlpatterns = [
    # pages
    path('', homepage, name='homepage'),
    path('loginPage/', loginPage, name='loginPage'),
    path('logout/', user_logout, name='logout'),
    path('postLogin/', postLogin, name='UserLogin'),

    ]