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


class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'datetime', 'lastUpdatedOn', 'isDeleted']


admin.site.register(Unit, UnitAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'datetime', 'lastUpdatedOn', 'isDeleted']


admin.site.register(Category, CategoryAdmin)


class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'datetime', 'lastUpdatedOn', 'isDeleted']


admin.site.register(Brand, BrandAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'stock', 'categoryID', 'brandID', 'unitID', 'cp', 'mrp', 'sp', 'datetime', 'lastUpdatedOn',
                    'isDeleted']


admin.site.register(Product, ProductAdmin)


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'gst', 'address', 'datetime', 'lastUpdatedOn', 'isDeleted']


admin.site.register(Supplier, SupplierAdmin)
