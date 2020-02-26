from django.http import HttpResponseRedirect,HttpResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr
from .verifylib import isvalidUserName,isValidEmail
from doca.settings import SECRET_KEY
import hashlib


db=boto3.resource('dynamodb')
def isDoctor(isDoctor=0):
    def is_authenticated(function):
        def wrapper_function(*args,**kwargs):
            if 'email' in args[0].session and 'isDoctor' in args[0].session and 'valid' in args[0].session and 'signature' in args[0].session:
                email = args[0].session['email']
                valid = args[0].session['valid']
                isDoctor0 = args[0].session['email']
                signature = args[0].session['signature']
                if (isValidEmail(email)==False):
                    return HttpResponseRedirect('/accounts/login/')
                gensignature = hashlib.sha256((email+str(isDoctor0)+valid+SECRET_KEY).encode).hexdigest()
                if (gensignature == signature and isDoctor == isDoctor0):
                    return function(*args,**kwargs)
            return HttpResponseRedirect("/accounts/login/")
        return wrapper_function
    return is_authenticated



def is_not_authenticated(function):
    def wrapper_function(*args,**kwargs):
        
        if 'email' in args[0].session and 'isDoctor' in args[0].session and 'valid' in args[0].session and 'signature' in args[0].session and 'isVerified' in args[0].session:
            email = args[0].session['email']
            valid = args[0].session['valid']
            isDoctor0 = args[0].session['email']
            signature = args[0].session['signature']
            isVerified = args[0].session['isVerified']
            if (isVerified == 0) :
                return HttpResponseRedirect('/accounts/verifyotp/')
            if (isValidEmail(email)==False):
                return function(*args,**kwargs)
            gensignature = hashlib.sha256((email+str(isDoctor0)+valid+str(isVerified)+SECRET_KEY).encode).hexdigest()

            if (gensignature == signature):
                if (isDoctor0 == 0):
                    return HttpResponse("<H1> Patient HomePage </H1>")
                return HttpResponse("<H1> Doctor HomePage </H1>")
        return function(*args,**kwargs)
    return wrapper_function
    

def is_authenticated_notverified(function):
    def wrapper_function(*args,**kwargs):
        if 'email' in args[0].session:
            user = args[0].session['email']
            print(user)
            table = db.Table('users')
            if(isValidEmail(user)):
                key = 'email' 
                response = table.scan(
                    FilterExpression=Attr(key).eq(user)
                )
                if response['Count'] != 0:
                    print(response['Items'][0]['isVerified'])
                    if(response['Items'][0]['isVerified'] == 0):
                        return function(*args,**kwargs)
        return HttpResponseRedirect("/accounts/login/")
    return wrapper_function



