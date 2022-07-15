from functools import wraps

from activation.models import Validity, EcomValidity
from django.contrib.auth import logout, authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import *
# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def check_group(group_name):
    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                return redirect('/')
            return view_func(request, *args, **kwargs)

        return wrapper

    return _check_group


def loginPage(request):
    # if not request.user.is_authenticated:
    return render(request, 'home/login.html')
    # else:
    #     return redirect('/admin_home/')


@check_group('Admin')
def admin_home(request):
    return render(request, 'home/admin/index.html')


@check_group('Collection')
def collection_home(request):
    return render(request, 'home/collection/indexCollection.html')


def user_list(request):
    groups = StaffGroup.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        'groups': groups
    }
    return render(request, 'home/admin/userList.html', context)


def product_list(request):
    units = Unit.objects.filter(isDeleted__exact=False).order_by('name')
    categories = Category.objects.filter(isDeleted__exact=False).order_by('name')
    brands = Brand.objects.filter(isDeleted__exact=False).order_by('name')

    context = {
        'units': units,
        'categories': categories,
        'brands': brands
    }
    return render(request, 'home/productList.html', context)


def purchase_list(request):
    return render(request, 'home/purchaseList.html')


def purchase_add(request):
    suppliers = Supplier.objects.filter(isDeleted__exact=False).order_by('name')
    products = Product.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'home/purchaseAdd.html', context)


def supplier_add(request):
    return render(request, 'home/supplierList.html')


def customer_list(request):
    return render(request, 'home/collection/customerListByStaff.html')


def customer_list_admin(request):
    return render(request, 'home/admin/customerListAdmin.html')


def customer_add(request):
    suppliers = Supplier.objects.filter(isDeleted__exact=False).order_by('name')
    products = Product.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'home/customerAdd.html', context)


def sales_add(request):
    return render(request, 'home/collection/saleAdd.html')


def sales_list(request):
    return render(request, 'home/collection/salesListByStaff.html')


def sales_list_admin(request):
    return render(request, 'home/admin/salesListByAdmin.html')


def user_logout(request):
    logout(request)
    return redirect("homeApp:loginPage")


def installment_list(request):
    return render(request, 'home/collection/installmentListByUser.html')


@csrf_exempt
def postLogin(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # if 'Admin' in request.user.groups.values_list('name', flat=True):
            return JsonResponse({'message': 'success', 'data': '/home/'}, safe=False)
            # elif 'Collection' in request.user.groups.values_list('name', flat=True):
            #     return JsonResponse({'message': 'success', 'data': '/collection/'}, safe=False)
        else:
            return JsonResponse({'message': 'fail'}, safe=False)

        # else:
        #     return JsonResponse({'message': 'fail'}, safe=False)
    else:
        return JsonResponse({'message': 'fail'}, safe=False)


def homepage(request):
    if request.user.is_authenticated:
        if 'Admin' in request.user.groups.values_list('name', flat=True):
            return redirect('/admin_home/')
        elif 'Collection' in request.user.groups.values_list('name', flat=True):
            return redirect('/collection_home/')
        else:
            try:
                val = Validity.objects.last()
                message = "Your License is Valid till {}".format(val.expiryDate.strftime('%d-%m-%Y'))
            except:
                message = "You are using a trial version."

            try:
                valEcom = EcomValidity.objects.last()
                messageEcom = "Your License is Valid till {}".format(valEcom.expiryDate.strftime('%d-%m-%Y'))
            except:
                messageEcom = "You are using a trial version."

            context = {
                'message': message,
                'messageEcom': messageEcom
            }

            return render(request, 'home/main.html', context)
