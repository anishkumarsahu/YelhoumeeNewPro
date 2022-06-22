from django.urls import path
from .views import *

urlpatterns = [
    # pages
    path(r'^$', activate, name='activate'),
    ]