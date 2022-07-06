import calendar
from django.core import management
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.template import loader
from django.template.defaultfilters import register
from django.utils.crypto import get_random_string
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from datetime import datetime, timedelta

from activation.models import Validity
from activation.views import is_activated, is_ecom_activated

from .models import *
from home.models import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape


@transaction.atomic
@csrf_exempt
def add_staff_api(request):
    if request.method == 'POST':
        try:
            CompanyUserName = request.POST.get("CompanyUserName")
            UserPhoneNo = request.POST.get("UserPhoneNo")
            UserEmail = request.POST.get("UserEmail")
            UserAddress = request.POST.get("UserAddress")
            UserGroup = request.POST.get("UserGroup")
            UserStatus = request.POST.get("UserStatus")
            UserPwd = request.POST.get("UserPwd")
            imageUpload = request.FILES["imageUpload"]

            staff = StaffUser()
            staff.photo = imageUpload
            staff.name = CompanyUserName
            staff.phone = UserPhoneNo
            staff.email = UserEmail
            staff.address = UserAddress
            staff.group = UserGroup
            staff.isActive = UserStatus
            staff.userPassword = UserPwd
            staff.save()
            username = 'USER' + get_random_string(length=3, allowed_chars='1234567890')
            while User.objects.filter(username__exact=username).count() > 0:
                username = 'USER' + get_random_string(length=5, allowed_chars='1234567890')
            else:
                new_user = User()
                new_user.username = username
                new_user.set_password(UserPwd)

                new_user.save()
                staff.username = username
                staff.user_ID_id = new_user.pk

                staff.save()

                try:
                    g = Group.objects.get(name=UserGroup)
                    g.user_set.add(new_user.pk)
                    g.save()

                except:
                    g = Group()
                    g.name = UserGroup
                    g.save()
                    g.user_set.add(new_user.pk)
                    g.save()
            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


class StaffUserListJson(BaseDatatableView):
    order_columns = ['photo', 'name', 'username', 'userPassword', 'group', 'phone', 'address', 'isActive', 'datetime']

    def get_initial_queryset(self):
        # if 'Admin' in self.request.user.groups.values_list('name', flat=True):
        return StaffUser.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(username__icontains=search)
                | Q(group__icontains=search) | Q(phone__icontains=search)
                | Q(address__icontains=search) | Q(isActive__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            images = '<img class="ui avatar image" src="{}">'.format(item.photo.thumbnail.url)

            action = '''<button style="font-size:10px;" onclick = "GetUserDetails('{}')" class="ui circular facebook icon button green">
                    <i class="pen icon"></i>
                  </button>
                  <button style="font-size:10px;" onclick ="delUser('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                    <i class="trash alternate icon"></i>
                  </button></td>'''.format(item.pk, item.pk),

            json_data.append([
                images,  # escape HTML for security reasons
                escape(item.name),
                escape(item.username),
                escape(item.userPassword),
                escape(item.group),
                escape(item.phone),
                escape(item.address),
                escape(item.isActive),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])

        return json_data


@transaction.atomic
@csrf_exempt
def delete_staff_user(request):
    if request.method == 'POST':
        try:
            id = request.POST.get("userID")
            staff = StaffUser.objects.get(pk=int(id))
            staff.isDeleted = True
            staff.save()
            new_user = User.objects.get(pk=staff.user_ID_id)
            new_user.is_active = False
            new_user.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


def get_staff_user_detail(request):
    id = request.GET.get('id')
    C_User = get_object_or_404(StaffUser, id=id)
    # instance = BankDetails.objects.get(companyID_id=company.pk)

    data = {
        'ID': C_User.pk,
        'UserName': C_User.name,
        'UserPhone': C_User.phone,
        'UserAddress': C_User.address,
        'UserEmail': C_User.email,
        'UserPassword': C_User.userPassword,
        'UserGroup': C_User.group,
        'IsActive': C_User.isActive,
        'ImgUrl': C_User.photo.medium.url

    }
    return JsonResponse({'data': data}, safe=False)


@transaction.atomic
@csrf_exempt
def edit_staff_api(request):
    if request.method == 'POST':
        try:
            EditUserId = request.POST.get("EditUserId")
            CompanyUserName = request.POST.get("CompanyUserName")
            UserPhoneNo = request.POST.get("UserPhoneNo")
            UserEmail = request.POST.get("UserEmail")
            UserAddress = request.POST.get("UserAddress")
            UserGroup = request.POST.get("UserGroup")
            UserStatus = request.POST.get("UserStatus")
            UserPwd = request.POST.get("UserPwd")

            staff = StaffUser.objects.get(pk=int(EditUserId))
            staff.name = CompanyUserName
            staff.phone = UserPhoneNo
            staff.email = UserEmail
            staff.address = UserAddress
            staff.group = UserGroup
            staff.isActive = UserStatus
            staff.userPassword = UserPwd
            staff.save()

            new_user = User.objects.get(pk=staff.user_ID_id)
            new_user.set_password(UserPwd)
            if UserStatus == 'Active':
                new_user.is_active = True
            else:
                new_user.is_active = False
            new_user.save()
            new_user.groups.clear()
            try:
                g = Group.objects.get(name=UserGroup)
                g.user_set.add(new_user.pk)
                g.save()

            except:
                g = Group()
                g.name = UserGroup
                g.save()
                g.user_set.add(new_user.pk)
                g.save()
            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


# ---------------------------------Product ----------------------------------------------------

@transaction.atomic
@csrf_exempt
def add_product_api(request):
    if request.method == 'POST':
        try:
            productName = request.POST.get("productName")
            stock = request.POST.get("stock")
            unit = request.POST.get("unit")
            category = request.POST.get("category")
            brand = request.POST.get("brand")
            cp = request.POST.get("cp")
            mrp = request.POST.get("mrp")
            sp = request.POST.get("sp")

            pro = Product()
            pro.name = productName
            pro.unitID = unit
            pro.categoryID = category
            pro.brandID = brand
            pro.stock = float(stock)
            pro.cp = float(cp)
            pro.mrp = float(mrp)
            pro.sp = float(sp)
            pro.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


class ProductListJson(BaseDatatableView):
    order_columns = ['name', 'stock', 'unitID', 'categoryID', 'brandID', 'cp', 'mrp', 'sp', 'datetime']

    def get_initial_queryset(self):
        # if 'Admin' in self.request.user.groups.values_list('name', flat=True):
        return Product.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(stock__icontains=search)
                | Q(unitID__icontains=search) | Q(categoryID__icontains=search)
                | Q(brandID__icontains=search) | Q(cp__icontains=search) |
                Q(mrp__icontains=search) | Q(sp__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            action = '''<button style="font-size:10px;" onclick = "GetUserDetails('{}')" class="ui circular facebook icon button green">
                    <i class="pen icon"></i>
                  </button>
                  <button style="font-size:10px;" onclick ="delUser('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                    <i class="trash alternate icon"></i>
                  </button></td>'''.format(item.pk, item.pk),

            json_data.append([
                escape(item.name),
                escape(item.stock),
                escape(item.unitID),
                escape(item.categoryID),
                escape(item.brandID),
                escape(item.cp),
                escape(item.mrp),
                escape(item.sp),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])

        return json_data


@transaction.atomic
@csrf_exempt
def delete_product(request):
    if request.method == 'POST':
        try:
            id = request.POST.get("userID")
            pro = Product.objects.get(pk=int(id))
            pro.isDeleted = True
            pro.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


def get_product_detail(request):
    id = request.GET.get('id')
    instance = get_object_or_404(Product, id=id)
    # instance = BankDetails.objects.get(companyID_id=company.pk)

    data = {
        'ID': instance.pk,
        'ProductName': instance.name,
        'Stock': instance.stock,
        'Unit': instance.unitID,
        'Category': instance.categoryID,
        'Brand': instance.brandID,
        'CP': instance.cp,
        'MRP': instance.mrp,
        'SP': instance.sp
    }
    return JsonResponse({'data': data}, safe=False)


@transaction.atomic
@csrf_exempt
def edit_product_api(request):
    if request.method == 'POST':
        try:
            Id = request.POST.get("EditUserId")
            productName = request.POST.get("productName")
            stock = request.POST.get("stock")
            unit = request.POST.get("unit")
            category = request.POST.get("category")
            brand = request.POST.get("brand")
            cp = request.POST.get("cp")
            mrp = request.POST.get("mrp")
            sp = request.POST.get("sp")

            pro = Product.objects.get(id=int(Id))
            pro.name = productName
            pro.unitID = unit
            pro.categoryID = category
            pro.brandID = brand
            pro.stock = float(stock)
            pro.cp = float(cp)
            pro.mrp = float(mrp)
            pro.sp = float(sp)
            pro.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


# ---------------------------------Supplier ----------------------------------------------------

@transaction.atomic
@csrf_exempt
def add_supplier_api(request):
    if request.method == 'POST':
        try:
            supplierName = request.POST.get("supplierName")
            phone = request.POST.get("phone")
            gst = request.POST.get("gst")
            address = request.POST.get("address")

            obj = Supplier()
            obj.name = supplierName
            obj.phone = phone
            obj.gst = gst
            obj.address = address
            obj.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


@transaction.atomic
@csrf_exempt
def delete_supplier(request):
    if request.method == 'POST':
        try:
            id = request.POST.get("userID")
            obj = Supplier.objects.get(pk=int(id))
            obj.isDeleted = True
            obj.save()
            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


class SupplierListJson(BaseDatatableView):
    order_columns = ['name', 'phone', 'gst', 'address', 'datetime']

    def get_initial_queryset(self):
        # if 'Admin' in self.request.user.groups.values_list('name', flat=True):
        return Supplier.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(phone__icontains=search)
                | Q(gst__icontains=search) | Q(addtress__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            action = '''<button style="font-size:10px;" onclick = "GetUserDetails('{}')" class="ui circular facebook icon button green">
                    <i class="pen icon"></i>
                  </button>
                  <button style="font-size:10px;" onclick ="delUser('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                    <i class="trash alternate icon"></i>
                  </button></td>'''.format(item.pk, item.pk),

            json_data.append([
                escape(item.name),
                escape(item.phone),
                escape(item.gst),
                escape(item.address),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])

        return json_data


def get_supplier_detail(request):
    id = request.GET.get('id')
    instance = get_object_or_404(Supplier, id=id)
    # instance = BankDetails.objects.get(companyID_id=company.pk)

    data = {
        'ID': instance.pk,
        'Name': instance.name,
        'Phone': instance.phone,
        'GST': instance.gst,
        'Address': instance.address,

    }
    return JsonResponse({'data': data}, safe=False)


@transaction.atomic
@csrf_exempt
def edit_supplier_api(request):
    if request.method == 'POST':
        try:
            Id = request.POST.get("EditUserId")
            supplierName = request.POST.get("supplierName")
            phone = request.POST.get("phone")
            gst = request.POST.get("gst")
            address = request.POST.get("address")

            obj = Supplier.objects.get(id=int(Id))
            obj.name = supplierName
            obj.phone = phone
            obj.gst = gst
            obj.address = address
            obj.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)