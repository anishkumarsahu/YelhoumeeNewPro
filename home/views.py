from django.shortcuts import render

# Create your views here.

def loginPage(request):
    if not request.user.is_authenticated:
        return render(request, 'home/log.html')
    else:
        return redirect('/')

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