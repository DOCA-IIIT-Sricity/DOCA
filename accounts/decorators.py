from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render
from doca.settings import SECRET_KEY
import hashlib
from datetime import datetime,timedelta
from mongodb.mongolib import Table


def isDoctor(isDoctor=0):
    def is_authenticated(function):
        def wrapper_function(*args,**kwargs):
            if'session_key' in args[0].session:
                session_key = args[0].session['session_key']
                table = Table("SessionStore") 
                response = table.scan(FilterExpression={
                    'session_key':session_key,
                    },   
                ).values()
                
                if response['Count'] == 0:
                    return HttpResponseRedirect('/accounts/login/')
                
                isDoctor0 = response['Items'][0]['isDoctor']
                isVerified = response['Items'][0]['isVerified']
                timestamp = response['Items'][0]['timestamp']
                email = response['Items'][0]['email']

                if (isVerified == 0) :
                    return HttpResponseRedirect('/accounts/verifyotp/')
                
                if (datetime.strptime(timestamp,"%Y%m%d%H%M%S")+timedelta(days=7) < datetime.now()):
                    table.delete(FilterExpression={'session_key':args[0].session['session_key']})
                    del args[0].session['session_key']
                    return HttpResponseRedirect("/accounts/login/")
                    
               
                if (isDoctor0 == isDoctor):
                    return function(*args,**kwargs)
                    
                    
            return HttpResponseRedirect("/accounts/login/")
        return wrapper_function
    return is_authenticated



def is_not_authenticated(function):
    def wrapper_function(*args,**kwargs):

        if'session_key' in args[0].session:
            session_key = args[0].session['session_key']
            table = Table("SessionStore") 
            response = table.scan(FilterExpression={
                'session_key':session_key,
                },
                
            ).values()
            
            if response['Count'] == 0:
                return function(*args,**kwargs)
            
            isDoctor0 = response['Items'][0]['isDoctor']
            isVerified = response['Items'][0]['isVerified']
            timestamp = response['Items'][0]['timestamp']
            email = response['Items'][0]['email']
            
            if (isVerified == 0) :
                return HttpResponseRedirect('/accounts/verifyotp/')
            
            
            if (datetime.strptime(timestamp,"%Y%m%d%H%M%S")+timedelta(days=7) < datetime.now()):
                return function(*args,**kwargs)
                          
            
            if (isDoctor0 == 0):
                return HttpResponse("<H1> Patient HomePage </H1>")
            return HttpResponse("<H1> Doctor HomePage </H1>")
        
        return function(*args,**kwargs)
    return wrapper_function
    

def is_authenticated_notverified(function):
    def wrapper_function(*args,**kwargs):
        print(args)
        if 'session_key' in args[0].session:
             
            session_key = args[0].session['session_key']
            table = Table("SessionStore") 
            response = table.scan(FilterExpression={
                'session_key':session_key,
                },  
            ).values()
            
            if response['Count'] == 0:
                print(session_key)
                return HttpResponseRedirect("/accounts/login/")
        
            isVerified = response['Items'][0]['isVerified']
            timestamp = response['Items'][0]['timestamp']
            email = response['Items'][0]['email']
            
            if (datetime.strptime(timestamp,"%Y%m%d%H%M%S")+timedelta(days=7) < datetime.now()):
                table.delete(FilterExpression={'session_key':args[0].session['session_key']})
                del args[0].session['session_key']
                return HttpResponseRedirect("/accounts/login/")
            
            if isVerified == 0 :
                
                print("isVerfied")
                return function(*args,**kwargs)
                 
        print("not Found")
        return HttpResponseRedirect("/accounts/login/")
    return wrapper_function



def getEmail(session_key):
    table = Table("SessionStore") 
    response = table.scan(FilterExpression={
        'session_key':session_key,
        },
        Projection=['email']  
    ).values()
    
    return response['Items'][0]['email']