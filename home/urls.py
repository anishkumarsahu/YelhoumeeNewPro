from django.urls import path
from .views import *

urlpatterns = [
    # pages
    path('home/', homepage, name='homepage'),
    path('', loginPage, name='loginPage'),
    path('logout/', user_logout, name='logout'),
    path('postLogin/', postLogin, name='UserLogin'),
    # admin
    path('admin_home/', admin_home, name='admin_home'),
    path('user_list/', user_list, name='user_list'),

]
