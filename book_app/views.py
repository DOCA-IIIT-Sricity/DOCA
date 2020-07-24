from django.shortcuts import render
from accounts.decorators import isDoctor,getEmail

@isDoctor(0)
def SearchDoctor(request):
    if "spec" in request.GET and "loc" in request.GET and 'date' in request.GET:
        specialization = request.GET['spec']
        location = request.GET['loc']
        date = request.GET['date']
        
    else:
        return render(request,'book_appointement/b_app_find.html')
    