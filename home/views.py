from activation.models import Validity, EcomValidity
from django.contrib.auth import logout, authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def loginPage(request):
    if not request.user.is_authenticated:
        return render(request, 'home/login.html')
    else:
        return redirect('/')

def user_logout(request):
    logout(request)
    return redirect("homeApp:loginPage")



@csrf_exempt
def postLogin(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if 'Admin' in request.user.groups.values_list('name',
                                                          flat=True) or 'Staff' in request.user.groups.values_list(
                    'name', flat=True):
                return JsonResponse({'message': 'success', 'data': '/'}, safe=False)
            elif 'Executive' in request.user.groups.values_list('name', flat=True):
                return JsonResponse({'message': 'success', 'data': '/ecom/home/'}, safe=False)
            else:
                return JsonResponse({'message': 'fail'}, safe=False)


        else:
            return JsonResponse({'message': 'fail'}, safe=False)
    else:
        return JsonResponse({'message': 'fail'}, safe=False)



def homepage(request):
    if request.user.is_authenticated:
        if 'Executive' in request.user.groups.values_list('name', flat=True):
            return redirect('/ecom/home/')

        else :
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
                'messageEcom':messageEcom
            }

            return render(request, 'home/main.html', context)