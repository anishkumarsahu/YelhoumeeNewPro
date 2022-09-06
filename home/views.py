import calendar
from datetime import datetime, timedelta
from functools import wraps

import xlwt
from activation.models import Validity
from activation.views import is_activated
from dateutil.relativedelta import relativedelta
from django.contrib.auth import logout, authenticate, login
from django.db.models import Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def login_or_logout(request, type):
    try:
        data = LoginAndLogoutStatus()
        data.statusType = type
        if request.user.username != 'anish':
            staff = StaffUser.objects.select_related().get(user_ID_id=request.user.pk)
            data.userID_id = staff.pk
            data.save()
    except:
        pass


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


@check_group('Both')
def admin_home(request):
    try:
        val = Validity.objects.last()
        message = "Your License is Valid till {}".format(val.expiryDate.strftime('%d-%m-%Y'))
    except:
        message = "You are using a trial version."

    context = {
        'message': message,
    }
    return render(request, 'home/admin/index.html', context)


@check_group('Collection')
def collection_home(request):
    return render(request, 'home/collection/indexCollection.html')


@check_group('Admin')
@is_activated()
def user_list(request):
    groups = StaffGroup.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        'groups': groups
    }
    return render(request, 'home/admin/userList.html', context)


@check_group('Both')
@is_activated()
def product_list(request):
    units = Unit.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    categories = Category.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    brands = Brand.objects.select_related().filter(isDeleted__exact=False).order_by('name')

    context = {
        'units': units,
        'categories': categories,
        'brands': brands
    }
    return render(request, 'home/admin/productList.html', context)


@check_group('Both')
@is_activated()
def purchase_list(request):
    return render(request, 'home/admin/purchaseList.html')


@check_group('Both')
@is_activated()
def purchase_add(request):
    suppliers = Supplier.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    products = Product.objects.select_related().filter(isDeleted__exact=False).order_by('name')
    context = {
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'home/admin/purchaseAdd.html', context)


@check_group('Both')
@is_activated()
def supplier_add(request):
    return render(request, 'home/admin/supplierList.html')


@check_group('Collection')
def customer_list(request):
    return render(request, 'home/collection/customerListByStaff.html')


@check_group('Both')
@is_activated()
def customer_list_admin(request):
    return render(request, 'home/admin/customerListAdmin.html')


@check_group('Collection')
def customer_add(request):
    # suppliers = Supplier.objects.filter(isDeleted__exact=False).order_by('name')
    # products = Product.objects.filter(isDeleted__exact=False).order_by('name')
    context = {
        # 'suppliers': suppliers,
        # 'products': products
    }
    return render(request, 'home/collection/customerAdd.html', context)


@check_group('Both')
@is_activated()
def customer_add_admin(request):
    context = {
    }
    return render(request, 'home/admin/customerAddAdmin.html', context)


@check_group('Both')
@is_activated()
def customer_edit_admin(request, id=None):
    instance = get_object_or_404(Customer, pk=id)
    context = {
        'instance': instance
    }
    return render(request, 'home/admin/customerEditAdmin.html', context)


@check_group('Collection')
def sales_add(request):
    return render(request, 'home/collection/saleAdd.html')


@check_group('Both')
@is_activated()
def sales_add_admin(request):
    users = StaffUser.objects.select_related().filter(isActive__exact='Active', isDeleted__exact=False,
                                                      group__exact='Collection').order_by('name')
    context = {
        'users': users
    }
    return render(request, 'home/admin/saleAddAdmin.html', context)


@check_group('Both')
@is_activated()
def sales_edit_admin(request, id=None):
    users = StaffUser.objects.select_related().filter(isActive__exact='Active', isDeleted__exact=False,
                                                      group__exact='Collection').order_by('name')
    instance = get_object_or_404(Sale, pk=id)
    context = {
        'users': users,
        'instance': instance
    }
    return render(request, 'home/admin/saleEditAdmin.html', context)


@check_group('Collection')
def sales_list(request):
    return render(request, 'home/collection/salesListByStaff.html')


@check_group('Both')
@is_activated()
def sales_list_admin(request):
    return render(request, 'home/admin/salesListByAdmin.html')


@check_group('Both')
@is_activated()
def report_admin(request):
    return render(request, 'home/admin/ReportSalesByAdmin.html')


@check_group('Both')
@is_activated()
def document_list_admin(request):
    return render(request, 'home/admin/documentList.html')


@check_group('Collection')
def sales_detail(request, id=None):
    instance = get_object_or_404(Sale, id=id)
    installments = Installment.objects.select_related().filter(isDeleted__exact=False,
                                                               saleID_id__exact=instance.pk).order_by(
        'installmentDate')
    context = {
        'instance': instance,
        'installments': installments
    }
    return render(request, 'home/collection/salesDetail.html', context)


@check_group('Both')
@is_activated()
def sales_detail_admin(request, id=None):
    instance = get_object_or_404(Sale, id=id)
    installments = Installment.objects.select_related().filter(isDeleted__exact=False,
                                                               saleID_id__exact=instance.pk).order_by(
        'installmentDate')
    context = {
        'instance': instance,
        'installments': installments
    }
    return render(request, 'home/admin/salesDetailAdmin.html', context)


@check_group('Collection')
def customer_detail(request, id=None):
    instance = get_object_or_404(Customer, id=id)
    sales = Sale.objects.select_related().filter(isDeleted__exact=False, customerID_id=instance.pk).order_by(
        '-pk')
    context = {
        'instance': instance,
        'sales': sales
    }
    return render(request, 'home/collection/customerDetail.html', context)


@check_group('Both')
@is_activated()
def customer_detail_admin(request, id=None):
    instance = get_object_or_404(Customer, id=id)
    sales = Sale.objects.select_related().filter(isDeleted__exact=False, customerID_id=instance.pk).order_by(
        '-pk')
    context = {
        'instance': instance,
        'sales': sales
    }
    return render(request, 'home/admin/customerDetailAdmin.html', context)


def user_logout(request):
    login_or_logout(request, 'Logout')
    logout(request)
    return redirect("homeApp:loginPage")


@check_group('Collection')
def installment_list(request):
    return render(request, 'home/collection/installmentListByUser.html')


@check_group('Both')
@is_activated()
def installment_list_admin(request):
    users = StaffUser.objects.select_related().filter(isActive__exact='Active', isDeleted__exact=False,
                                                      group__exact='Collection').order_by('name')
    context = {
        'users': users
    }
    return render(request, 'home/admin/installmentListAdmin.html', context)


@check_group('Collection')
def my_profile(request):
    instance = get_object_or_404(StaffUser, user_ID_id=request.user.pk)
    context = {
        'instance': instance
    }
    return render(request, 'home/collection/profile.html', context)


def my_profile_admin(request):
    instance = get_object_or_404(StaffUser, user_ID_id=request.user.pk)
    context = {
        'instance': instance
    }
    return render(request, 'home/admin/profileAdmin.html', context)


@csrf_exempt
def postLogin(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            login_or_logout(request, 'Login')
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
        if 'Both' in request.user.groups.values_list('name', flat=True):
            return redirect('/admin_home/')
        elif 'Collection' in request.user.groups.values_list('name', flat=True):
            return redirect('/collection_home/')
        else:

            return render(request, 'home/login.html')


@check_group('Both')
@is_activated()
def login_logout_report_admin(request, id=None):
    return render(request, 'home/admin/loginLogoutList.html')


def download_sales_report(request):
    status = request.GET.get('status')
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')
    sDate = datetime.strptime(startDate, '%m/%Y')
    eDate = datetime.strptime(endDate, '%m/%Y')

    s = datetime(sDate.year, sDate.month, 1)
    ssDate = datetime.strptime(str(s.strftime("%d/%m/%Y")), '%d/%m/%Y')

    x = calendar.monthrange(eDate.year, eDate.month)[1]
    e = datetime(eDate.year, eDate.month, x)
    eeDate = datetime.strptime(str(e.strftime("%d/%m/%Y")), '%d/%m/%Y')
    if status == 'All':
        sales = Sale.objects.select_related().filter(isDeleted__exact=False, installmentStartDate__range=(
            ssDate.date(), eeDate.date() + timedelta(days=1))).order_by('installmentStartDate')
        tenure = Sale.objects.select_related().filter(isDeleted__exact=False, installmentStartDate__range=(
            ssDate.date(), eeDate.date() + timedelta(days=1))).aggregate(Max('tenureInMonth'))
    elif status == 'Opened':
        sales = Sale.objects.select_related().filter(isDeleted__exact=False, installmentStartDate__range=(
            ssDate.date(), eeDate.date() + timedelta(days=1)), isClosed=False).order_by('installmentStartDate')
        tenure = Sale.objects.select_related().filter(isDeleted__exact=False, installmentStartDate__range=(
            ssDate.date(), eeDate.date() + timedelta(days=1)), isClosed=False).aggregate(Max('tenureInMonth'))
    elif status == 'Closed':
        sales = Sale.objects.select_related().filter(isDeleted__exact=False, installmentStartDate__range=(
            ssDate.date(), eeDate.date() + timedelta(days=1)), isClosed=True).order_by('installmentStartDate')
        tenure = Sale.objects.select_related().filter(isDeleted__exact=False, installmentStartDate__range=(
            ssDate.date(), eeDate.date() + timedelta(days=1)), isClosed=True).aggregate(Max('tenureInMonth'))
    else:
        pass
    ins_month_list = []

    columns = ['Invoice Date', 'CustomerID', 'Customer Name', 'Address', 'District', 'Contact No.', 'Alt No.',
               'Item Name'
        , 'Delivered By', 'Staff Assigned for Collection', 'DOC', 'Advance', 'Inst. Amount', 'Tenure', 'Total Amount',
               'Overall Paid', 'Balance', ]

    try:
        t = tenure['tenureInMonth__max']
        if t is None:
            t = 0
    except:
        t = 0
    counter = 0
    for i in range(int(t)):
        month_year = ssDate.date() + relativedelta(months=+i)
        columns.insert(len(columns) - 2, month_year.strftime("%y%b"))
        ins_month_list.append(month_year)
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename=SalesReport.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('SalesWise')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    row_num = 0
    for sa in sales:

        row_num = row_num + 1
        ws.write(row_num, 0, str(sa.datetime.strftime('%d-%m-%Y')), font_style)
        ws.write(row_num, 1, sa.customerID.customerCode, font_style)
        ws.write(row_num, 2, sa.customerName, font_style)
        ws.write(row_num, 3, sa.customerID.address, font_style)
        ws.write(row_num, 4, sa.customerID.district, font_style)
        ws.write(row_num, 5, sa.customerID.phoneNumber, font_style)
        ws.write(row_num, 6, '', font_style)
        ws.write(row_num, 7, sa.productName, font_style)
        ws.write(row_num, 8, sa.addedBy.name, font_style)
        ws.write(row_num, 9, sa.assignedTo.name, font_style)
        ws.write(row_num, 10, str(sa.installmentStartDate.strftime('%d-%m-%Y')), font_style)
        ws.write(row_num, 11, sa.advancePaid, font_style)
        ws.write(row_num, 12, sa.emiAmount, font_style)
        ws.write(row_num, 13, sa.tenureInMonth, font_style)
        ws.write(row_num, 14, sa.totalAmount, font_style)
        month = 1
        for i in ins_month_list:
            ins_month_total = 0.0
            ins = Installment.objects.select_related().filter(saleID_id=sa.pk, isDeleted=False,
                                                              installmentDate__month=i.month,
                                                              installmentDate__year=i.year, isPaid=True)
            for t in ins:
                ins_month_total = ins_month_total + t.paidAmount

            ws.write(row_num, 14 + month, ins_month_total, font_style)
            month = month + 1
        ws.write(row_num, 15 + len(ins_month_list), sa.amountPaid, font_style)
        ws.write(row_num, 16 + len(ins_month_list), (sa.totalAmount - sa.amountPaid), font_style)
    # ws.write(row_num + 1, 3, "Grand Total", font_style)
    # ws.write(row_num + 1, 4, grandTatal, font_style)
    wb.save(response)
    return response
