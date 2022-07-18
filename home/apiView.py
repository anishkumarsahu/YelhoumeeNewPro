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


# ----------------------------------Purchase------------------------

@csrf_exempt
@transaction.atomic
def add_purchase_api(request):
    if request.method == 'POST':
        taxable = request.POST.get("taxable")
        totalGst = request.POST.get("totalGst")
        otherCharges = request.POST.get("otherCharges")
        roundOff = request.POST.get("roundOff")
        grandTotal = request.POST.get("grandTotal")
        supplierNameID = request.POST.get("supplierNameID")
        invoice = request.POST.get("invoice")
        idate = request.POST.get("idate")
        datas = request.POST.get("datas")
        pur = Purchase()
        s = str(supplierNameID).split('|')
        pur.supplierID_id = int(s[1])
        pur.supplierName = s[0]
        pur.taxableAmount = float(taxable)
        pur.gstAmount = float(totalGst)
        pur.otherCharges = float(otherCharges)
        pur.roundOff = float(roundOff)
        pur.grandTotal = float(grandTotal)
        pur.invoiceNumber = invoice
        pur.invoiceDate = datetime.strptime(idate, '%d/%m/%Y')
        pur.save()

        splited_receive_item = datas.split("@")
        for item in splited_receive_item[:-1]:
            item_details = item.split('|')
            p = PurchaseProduct()
            p.purchaseID_id = pur.pk
            p.productID_id = int(item_details[0])
            p.productName = item_details[1]
            p.quantity = float(item_details[2])
            p.rate = float(item_details[3])
            p.gst = float(item_details[4])
            p.net = float(item_details[5])
            p.total = float(item_details[6])
            pro = Product.objects.get(pk=int(int(item_details[0])))
            ori_stock = pro.stock
            pro.stock = (ori_stock + float(item_details[2]))
            pro.save()
            p.save()
        return JsonResponse({'message': 'success'}, safe=False)


class PurchaseListJson(BaseDatatableView):
    order_columns = ['supplierName', 'invoiceNumber', 'invoiceDate', 'taxableAmount', 'gstAmount', 'otherCharges',
                     'roundOff', 'grandTotal', 'datetime']

    def get_initial_queryset(self):
        # if 'Admin' in self.request.user.groups.values_list('name', flat=True):
        return Purchase.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(supplierName__icontains=search) | Q(invoiceNumber__icontains=search)
                | Q(invoiceDate__icontains=search) | Q(grandTotal__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            action = '''<button style="font-size:10px;" onclick = "GetPurchaseDetail('{}')" class="ui circular facebook icon button green">
                    <i class="receipt icon"></i>
                  </button>
                  <button style="font-size:10px;" onclick ="delUser('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                    <i class="trash alternate icon"></i>
                  </button></td>'''.format(item.pk, item.pk),

            json_data.append([
                escape(item.supplierName),
                escape(item.invoiceNumber),
                escape(item.invoiceDate.strftime('%d-%m-%Y')),
                escape(item.taxableAmount),
                escape(item.gstAmount),
                escape(item.otherCharges),
                escape(item.roundOff),
                escape(item.grandTotal),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])

        return json_data


def get_purchase_detail(request, id=None):
    instance = get_object_or_404(Purchase, pk=id)
    basic = {
        'Name': instance.supplierName,
        'Gst': instance.supplierID.gst,
        'Phone': instance.supplierID.phone,
        'Address': instance.supplierID.address,
    }
    items = PurchaseProduct.objects.filter(purchaseID_id=instance.pk)
    item_list = []
    for i in items:
        item_dic = {
            'ItemID': i.pk,
            'ItemProductName': i.productName,
            'ItemQuantity': i.quantity,
            'ItemRate': i.rate,
            'ItemGst': i.gst,
            'ItemnetRate': i.net,
            'ItemTotal': i.total,

        }
        item_list.append(item_dic)

    data = {
        'Basic': basic,
        'Items': item_list

    }
    return JsonResponse({'data': data}, safe=False)


@csrf_exempt
@transaction.atomic
def delete_purchase(request):
    if request.method == 'POST':
        id = request.POST.get("ID")
        print(id)
        sale = Purchase.objects.get(pk=int(id))
        sale.isDeleted = True
        sale.save()
        sales_products = PurchaseProduct.objects.filter(purchaseID_id=int(id))
        for pro in sales_products:
            product = Product.objects.get(pk=pro.productID_id)
            product.stock = product.stock - pro.quantity
            product.save()
        return JsonResponse({'message': 'success'}, safe=False)


# ---------------------------------customer------------------------------------

@transaction.atomic
@csrf_exempt
def add_customer_api(request):
    if request.method == 'POST':
        try:
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            district = request.POST.get("district")
            address = request.POST.get("address")
            lat = request.POST.get("lat")
            lng = request.POST.get("lng")
            photo = request.FILES["photo"]
            idf = request.FILES["idf"]
            idb = request.FILES["idb"]

            obj = Customer()
            obj.latitude = lat
            obj.longitude = lng
            obj.name = name
            obj.phoneNumber = phone
            obj.district = district
            obj.address = address
            obj.photo = photo
            obj.idProofFront = idf
            obj.idProofBack = idb
            user = StaffUser.objects.get(user_ID_id=request.user.pk)
            obj.addedBy_id = user.pk
            obj.save()
            obj.customerCode = str(obj.pk).zfill(5)
            obj.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


class CustomerListByUserJson(BaseDatatableView):
    order_columns = ['photo', 'name', 'customerCode', 'phoneNumber', 'district', 'address',
                     'idProofFront', 'idProofBack', 'datetime']

    def get_initial_queryset(self):
        try:
            startDateV = self.request.GET.get("startDate")
            endDateV = self.request.GET.get("endDate")
            sDate = datetime.strptime(startDateV, '%d/%m/%Y')
            eDate = datetime.strptime(endDateV, '%d/%m/%Y')

            return Customer.objects.filter(isDeleted__exact=False, addedBy__user_ID_id__exact=self.request.user.pk,
                                           datetime__range=(sDate.date(), eDate.date() + timedelta(days=1)))

        except:

            return Customer.objects.filter(isDeleted__exact=False, addedBy__user_ID_id__exact=self.request.user.pk)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(customerCode__icontains=search) | Q(district__icontains=search) | Q(address__icontains=search)
                | Q(phoneNumber__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []

        for item in qs:
            photo = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.photo.large.url, item.photo.thumbnail.url)
            idProofFront = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.idProofFront.large.url, item.idProofFront.thumbnail.url)
            idProofBack = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.idProofBack.large.url, item.idProofBack.thumbnail.url)
            json_data.append([
                photo,  # escape HTML for security reasons
                escape(item.name),
                escape(item.customerCode),
                escape(item.phoneNumber),
                escape(item.district),
                escape(item.address),
                idProofFront,
                idProofBack,
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
            ])
        return json_data


class CustomerListJson(BaseDatatableView):
    order_columns = ['photo', 'name', 'customerCode', 'phoneNumber', 'district', 'address',
                     'idProofFront', 'idProofBack', 'datetime']

    def get_initial_queryset(self):
        try:
            startDateV = self.request.GET.get("startDate")
            endDateV = self.request.GET.get("endDate")
            sDate = datetime.strptime(startDateV, '%d/%m/%Y')
            eDate = datetime.strptime(endDateV, '%d/%m/%Y')

            return Customer.objects.filter(isDeleted__exact=False,
                                           datetime__range=(sDate.date(), eDate.date() + timedelta(days=1)))

        except:

            return Customer.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(customerCode__icontains=search) | Q(district__icontains=search) | Q(address__icontains=search)
                | Q(phoneNumber__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []

        for item in qs:
            photo = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.photo.large.url, item.photo.thumbnail.url)
            idProofFront = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.idProofFront.large.url, item.idProofFront.thumbnail.url)
            idProofBack = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.idProofBack.large.url, item.idProofBack.thumbnail.url)
            json_data.append([
                photo,  # escape HTML for security reasons
                escape(item.name),
                escape(item.customerCode),
                escape(item.phoneNumber),
                escape(item.district),
                escape(item.address),
                idProofFront,
                idProofBack,
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
            ])
        return json_data


# customer and product API list
def list_customer_api(request):
    try:
        obj_list = Customer.objects.filter(isDeleted__exact=False).order_by('name')
        o_list = []
        for obj in obj_list:
            obj_dic = {
                'ID': obj.pk,
                'Name': obj.name,
                'District': obj.district,
                'Address': obj.address,
                'Phone': obj.phoneNumber,
                'Detail': obj.name + ' - ' + obj.address + ' @ ' + str(obj.pk),
                'DisplayDetail': obj.name + ' - ' + obj.address
            }
            o_list.append(obj_dic)

        return JsonResponse({'message': 'success', 'data': o_list}, safe=False)
    except:
        return JsonResponse({'message': 'error'}, safe=False)


def list_product_api(request):
    try:
        obj_list = Product.objects.filter(isDeleted__exact=False).order_by('name')

        o_list = []
        for obj in obj_list:
            obj_dic = {
                'ID': obj.pk,
                'Name': obj.name,
                'Category': obj.categoryID,
                'NetTotal': obj.sp,
                'Detail': obj.name + ' - ' + obj.categoryID + ' @' + str(obj.pk),
                'DisplayDetail': obj.name + ' - ' + obj.categoryID + ' - ' + obj.brandID + ' (₹ {})'.format(obj.sp)
            }
            o_list.append(obj_dic)

        return JsonResponse({'message': 'success', 'data': o_list}, safe=False)
    except:
        return JsonResponse({'message': 'error'}, safe=False)


# -----------------------------------sales-----------------------------------------
@transaction.atomic
@csrf_exempt
def add_sales_api(request):
    if request.method == 'POST':
        try:
            photo = request.FILES["photo"]
            customer = request.POST.get("customer")
            product = request.POST.get("product")
            emi = request.POST.get("emi")
            advance = request.POST.get("advance")
            tenure = request.POST.get("tenure")
            totalAmount = request.POST.get("totalAmount")
            lat = request.POST.get("lat")
            lng = request.POST.get("lng")
            remark = request.POST.get("remark")
            idate = request.POST.get("idate")
            c = str(customer).split('@')
            cus = Customer.objects.get(pk=int(c[1]))
            p = str(product).split('@')
            pro = Product.objects.get(pk=int(p[1]))
            obj = Sale()
            obj.latitude = lat
            obj.longitude = lng
            obj.customerName = cus.name
            obj.customerID_id = cus.pk
            obj.productName = pro.name
            obj.productID_id = pro.pk
            obj.unit = pro.unitID
            obj.quantity = 1
            obj.rate = pro.sp
            obj.advancePaid = float(advance)
            obj.amountPaid = float(advance)
            obj.tenureInMonth = float(tenure)
            obj.emiAmount = float(emi)
            obj.totalAmount = float(totalAmount)
            obj.remark = remark
            obj.deliveryPhoto = photo
            user = StaffUser.objects.get(user_ID_id=request.user.pk)
            obj.addedBy_id = user.pk
            obj.assignedTo_id = user.pk
            obj.installmentStartDate = datetime.strptime(idate, '%d/%m/%Y')
            obj.save()
            pro.stock = pro.stock - 1
            pro.save()
            for i in range(0, int(tenure)):
                inst = Installment()
                inst.saleID_id = obj.pk
                inst.assignedTo_id = user.pk
                inst.installmentDate = obj.installmentStartDate + timedelta(days=(i + 1) * 30)
                inst.save()

            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)


class SalesListByUserJson(BaseDatatableView):
    order_columns = ['deliveryPhoto', 'customerName', 'productName', 'advancePaid', 'tenureInMonth', 'emiAmount',
                     'totalAmount',
                     'amountPaid', 'installmentStartDate', 'datetime']

    def get_initial_queryset(self):
        try:
            startDateV = self.request.GET.get("startDate")
            endDateV = self.request.GET.get("endDate")
            sDate = datetime.strptime(startDateV, '%d/%m/%Y')
            eDate = datetime.strptime(endDateV, '%d/%m/%Y')

            return Sale.objects.filter(isDeleted__exact=False, addedBy__user_ID_id__exact=self.request.user.pk,
                                       datetime__range=(sDate.date(), eDate.date() + timedelta(days=1)))

        except:

            return Sale.objects.filter(isDeleted__exact=False, addedBy__user_ID_id__exact=self.request.user.pk)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(customerName__icontains=search) | Q(customerID_customerCode__icontains=search)
                | Q(productName__icontains=search) | Q(advancePaid__icontains=search) | Q(
                    tenureInMonth__icontains=search)
                | Q(emiAmount__icontains=search) | Q(totalAmount__icontains=search) | Q(amountPaid__icontains=search)
                | Q(datetime__icontains=search) | Q(remark__icontains=search) | Q(
                    installmentStartDate__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            photo = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.deliveryPhoto.large.url, item.deliveryPhoto.thumbnail.url)
            action = '''<a style="font-size:10px;" href="/sales_detail/{}/" class="ui circular facebook icon button green">
                    <i class="receipt icon"></i>
                  </a>
                 </td>'''.format(item.pk),
            json_data.append([
                photo,  # escape HTML for security reasons
                escape(item.customerName),
                escape(item.productName),
                escape(item.advancePaid),
                escape(item.tenureInMonth),
                escape(item.emiAmount),
                escape(item.totalAmount),
                escape(item.amountPaid),
                escape(item.installmentStartDate.strftime('%d-%m-%Y')),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action
            ])
        return json_data


class SalesListAdminJson(BaseDatatableView):
    order_columns = ['deliveryPhoto', 'customerName', 'productName', 'advancePaid', 'tenureInMonth', 'emiAmount',
                     'totalAmount',
                     'amountPaid', 'installmentStartDate', 'datetime']

    def get_initial_queryset(self):
        try:
            startDateV = self.request.GET.get("startDate")
            endDateV = self.request.GET.get("endDate")
            sDate = datetime.strptime(startDateV, '%d/%m/%Y')
            eDate = datetime.strptime(endDateV, '%d/%m/%Y')

            return Sale.objects.filter(isDeleted__exact=False,
                                       datetime__range=(sDate.date(), eDate.date() + timedelta(days=1)))

        except:

            return Sale.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(customerName__icontains=search) | Q(customerID_customerCode__icontains=search)
                | Q(productName__icontains=search) | Q(advancePaid__icontains=search) | Q(
                    tenureInMonth__icontains=search)
                | Q(emiAmount__icontains=search) | Q(totalAmount__icontains=search) | Q(amountPaid__icontains=search)
                | Q(datetime__icontains=search) | Q(remark__icontains=search) | Q(
                    installmentStartDate__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            photo = '''<img style="cursor:pointer" onclick="showImgModal('{}')" class="ui avatar image" src="{}">'''.format(
                item.deliveryPhoto.large.url, item.deliveryPhoto.thumbnail.url)
            action = '''<button style="font-size:10px;" onclick = "GetPurchaseDetail('{}')" class="ui circular facebook icon button green">
                    <i class="receipt icon"></i>
                  </button>
                  <button style="font-size:10px;" onclick ="delUser('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                    <i class="trash alternate icon"></i>
                  </button></td>'''.format(item.pk, item.pk),
            json_data.append([
                photo,  # escape HTML for security reasons
                escape(item.customerName),
                escape(item.productName),
                escape(item.advancePaid),
                escape(item.tenureInMonth),
                escape(item.emiAmount),
                escape(item.totalAmount),
                escape(item.amountPaid),
                escape(item.installmentStartDate.strftime('%d-%m-%Y')),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action
            ])
        return json_data


# ------------------------------------Installments-----------------------------------

class InstallmentListByUserJson(BaseDatatableView):
    order_columns = ['saleID.customerName', 'saleID.emiAmount', 'installmentDate', 'amountPaid', 'isPaid',
                     'isReassigned'
        , 'remark', 'paymentReceivedOn']

    def get_initial_queryset(self):
        try:
            startDateV = self.request.GET.get("startDate")
            endDateV = self.request.GET.get("endDate")
            sDate = datetime.strptime(startDateV, '%d/%m/%Y')
            eDate = datetime.strptime(endDateV, '%d/%m/%Y')

            return Installment.objects.filter(isDeleted__exact=False,
                                              assignedTo__user_ID_id__exact=self.request.user.pk,
                                              installmentDate__range=(sDate.date(), eDate.date() + timedelta(days=1)),
                                              saleID__isClosed__exact=False
                                              )
        except:

            return Installment.objects.filter(isDeleted__exact=False,
                                              assignedTo__user_ID_id__exact=self.request.user.pk,
                                              installmentDate__exact=datetime.today().date(),
                                              saleID__isClosed__exact=False
                                              )

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(saleID__customerName__icontains=search) | Q(saleID__productName__icontains=search)
                | Q(installmentDate__icontains=search) | Q(remark__icontains=search) | Q(amountPaid__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            action = '''<button style="font-size:10px;" onclick = "GetDetail('{}')" class="ui circular facebook icon button orange">
                    <i class="hand holding usd icon"></i>
                  </button>
                  <a style="font-size:10px;" href="/sales_detail/{}/" class="ui circular facebook icon button green">
                    <i class="receipt icon"></i>
                  </a>
                 '''.format(item.pk, item.saleID.pk),
            if item.isPaid == True:
                paid = '<button class="ui tiny active green button" type="button" >  Yes </button>'
                r_time = escape(item.paymentReceivedOn.strftime('%d-%m-%Y %I:%M %p')),
            else:
                paid = '<button class="ui tiny active red button" type="button" >  No </button>'
                r_time = '-'

            if item.isReassigned == True:
                isReassigned = '<button class="ui tiny active green button" type="button" >  Yes </button>'
            else:
                isReassigned = '<button class="ui tiny active red button" type="button" >  No </button>'
            json_data.append([
                escape(item.saleID.customerName),
                escape(item.saleID.emiAmount),
                escape(item.installmentDate.strftime('%d-%m-%Y')),
                escape(item.amountPaid),
                paid,
                isReassigned,
                escape(item.remark),
                r_time,
                action
            ])
        return json_data


def get_installment_detail(request):
    id = request.GET.get('id')
    instance = get_object_or_404(Installment, id=id)

    data = {
        'ID': instance.pk,
        'Name': instance.saleID.customerName,
        'Amount': instance.saleID.emiAmount
    }
    return JsonResponse({'data': data}, safe=False)
