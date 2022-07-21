from django.urls import path
from .views import *
from .apiView import *

urlpatterns = [
    # pages
    path('home/', homepage, name='homepage'),
    path('', loginPage, name='loginPage'),
    path('logout/', user_logout, name='logout'),
    path('postLogin/', postLogin, name='UserLogin'),

    # collection
    path('collection_home/', collection_home, name='collection_home'),
    path('customer_list_admin/', customer_list_admin, name='customer_list_admin'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customer_add/', customer_add, name='customer_add'),
    path('sales_add/', sales_add, name='sales_add'),
    path('sales_list/', sales_list, name='sales_list'),
    path('sales_list_admin/', sales_list_admin, name='sales_list_admin'),

    path('customer_detail/<int:id>/', customer_detail, name='customer_detail'),
    path('sales_detail/<int:id>/', sales_detail, name='sales_detail'),
    path('installment_list/', installment_list, name='installment_list'),
    path('my_profile/', my_profile, name='my_profile'),

    # admin
    path('my_profile_admin/', my_profile_admin, name='my_profile_admin'),
    path('admin_home/', admin_home, name='admin_home'),
    path('user_list/', user_list, name='user_list'),
    path('product_list/', product_list, name='product_list'),
    path('purchase_list/', purchase_list, name='purchase_list'),
    path('purchase_add/', purchase_add, name='purchase_add'),
    path('supplier_add/', supplier_add, name='supplier_add'),
    path('installment_list_admin/', installment_list_admin, name='installment_list_admin'),
    path('sales_detail_admin/<int:id>/', sales_detail_admin, name='sales_detail_admin'),

    # api Staff
    path('api/add_staff_api/', add_staff_api, name='add_staff_api'),
    path('api/delete_staff_user/', delete_staff_user, name='delete_staff_user'),
    path('api/get_staff_user_detail/', get_staff_user_detail, name='get_staff_user_detail'),
    path('api/edit_staff_api/', edit_staff_api, name='edit_staff_api'),
    path('api/StaffUserListJson/', StaffUserListJson.as_view(), name='StaffUserListJson'),

    # api Product
    path('api/add_product_api/', add_product_api, name='add_product_api'),
    path('api/delete_product/', delete_product, name='delete_product'),
    path('api/get_product_detail/', get_product_detail, name='get_product_detail'),
    path('api/edit_product_api/', edit_product_api, name='edit_product_api'),
    path('api/ProductListJson/', ProductListJson.as_view(), name='ProductListJson'),

    # api Supplier
    path('api/add_supplier_api/', add_supplier_api, name='add_supplier_api'),
    path('api/delete_supplier/', delete_supplier, name='delete_supplier'),
    path('api/get_supplier_detail/', get_supplier_detail, name='get_supplier_detail'),
    path('api/edit_supplier_api/', edit_supplier_api, name='edit_supplier_api'),
    path('api/SupplierListJson/', SupplierListJson.as_view(), name='SupplierListJson'),

    # api purchase
    path('api/list_product_api/', list_product_api, name='list_product_api'),
    path('api/add_purchase_api/', add_purchase_api, name='add_purchase_api'),
    path('api/delete_purchase/', delete_purchase, name='delete_purchase'),
    path('api/get_purchase_detail/<int:id>/', get_purchase_detail, name='get_purchase_detail'),
    path('api/PurchaseListJson/', PurchaseListJson.as_view(), name='PurchaseListJson'),

    # api Customer
    path('api/list_customer_api/', list_customer_api, name='list_customer_api'),
    path('api/add_customer_api/', add_customer_api, name='add_customer_api'),
    path('api/CustomerListByUserJson/', CustomerListByUserJson.as_view(), name='CustomerListByUserJson'),
    path('api/CustomerListJson/', CustomerListJson.as_view(), name='CustomerListJson'),

    # sales
    path('api/add_sales_api/', add_sales_api, name='add_sales_api'),
    path('api/SalesListByUserJson/', SalesListByUserJson.as_view(), name='SalesListByUserJson'),
    path('api/SalesListAdminJson/', SalesListAdminJson.as_view(), name='SalesListAdminJson'),

    # installments
    path('api/InstallmentListByAdminJson/', InstallmentListByAdminJson.as_view(), name='InstallmentListByAdminJson'),
    path('api/InstallmentListByUserJson/', InstallmentListByUserJson.as_view(), name='InstallmentListByUserJson'),
    path('api/get_installment_detail/', get_installment_detail, name='get_installment_detail'),
    path('api/add_installment_api/', add_installment_api, name='add_installment_api'),

    # report dashboard
    path('api/get_collection_user_report_api/', get_collection_user_report_api, name='get_collection_user_report_api'),

    path('api/get_admin_report_api/', get_admin_report_api, name='get_admin_report_api'),

]
