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

    
class ProductListForImageJson(BaseDatatableView):
    order_columns = ['name', 'brand', 'categoryID', 'mrp', 'cost', 'spWithoutGst', 'spWithGst', 'barcode']

    def get_initial_queryset(self):
        if 'Admin' in self.request.user.groups.values_list('name', flat=True):

            return Product.objects.filter(wareHouse_ID__isDeleted__exact=False, company_ID__isDeleted__exact=False,
                                          isDeleted__exact=False)
        else:
            user = CompanyUser.objects.get(user_ID_id=self.request.user.pk)
            return Product.objects.filter(wareHouse_ID__isDeleted__exact=False, company_ID__isDeleted__exact=False,
                                          isDeleted__exact=False, company_ID_id=user.company_ID_id,
                                          productType__iexact='Normal')

    def filter_queryset(self, qs):

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(brand__icontains=search)
                | Q(categoryID__name__icontains=search) | Q(mrp__icontains=search)
                | Q(cost__icontains=search) | Q(spWithoutGst__icontains=search)
                | Q(spWithGst__icontains=search)
            ).order_by('-id')

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            images = '<button class="mini ui red button">No Image Added</button>'
            img = ProductImage.objects.filter(productID_id=item.pk, isDeleted__exact=False)
            if img.count() < 1:
                images = '<button class="mini ui red button">No Image Added</button>'
            else:
                images = ''
                for i in img:
                    images += '<img class="ui avatar image" src="{}">'.format(i.productImage.thumbnail.url)

            if 'Admin' in self.request.user.groups.values_list('name', flat=True):
                action = '''
                    <button style="font-size:10px;" onclick = "GetProductImageDetail('{}')" class="ui circular facebook icon button green">
                                               <i class="image icon"></i>
                                             </button>

                        '''.format(item.pk),
            else:
                action = '<button class="mini ui button">Denied</button>'

            json_data.append([
                escape(item.name),  # escape HTML for security reasons
                escape(item.brand),
                escape(item.categoryID.name),
                escape(item.mrp),
                escape(item.cost),
                escape(item.spWithoutGst),
                escape(item.spWithGst),
                images,
                action,

            ])
        return json_data
