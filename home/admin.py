from django.contrib import admin

# Register your models here.
from .models import *


class StaffGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'datetime', 'lastUpdatedOn', 'isDeleted']


admin.site.register(StaffGroup, StaffGroupAdmin)


class StaffUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address', 'email', 'username', 'userPassword', 'group', 'isActive', 'datetime',
                    'lastUpdatedOn']


admin.site.register(StaffUser, StaffUserAdmin)
