from django.shortcuts import render
from accounts.decorators import isDoctor,getEmail
from mongodb.mongolib import Table

@isDoctor(0)
def SearchDoctor(request):
    if "spec" in request.GET and "loc" in request.GET and 'date' in request.GET:
        specialization = request.GET['spec']
        city = request.GET['city']
        date = request.GET['date']
        
        table = Table('doctor')
        
        results = table.scan(FilterExpression={"spec":specialization,'city':city}).values()
        data=[]
        
        for result in results['Items']:
            
        
            pass
        
        
    else:
        return render(request,'book_appointement/b_app_find.html')
    