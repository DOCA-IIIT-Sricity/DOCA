from django.http import HttpResponseRedirect
import boto3
from boto3.dynamodb.conditions import Key, Attr
from .verifylib import isvalidUserName,isValidEmail

db=boto3.resource('dynamodb')
def isDoctor(isDoctor=0):
    def is_authenticated(function):
        def wrapper_function(*args,**kwargs):
            if 'user' in args[0].session:
                user = args[0].session['user']
                table = db.Table('users')
                if(isValidEmail(user) or isvalidUserName(user)):
                    key = 'email' if isValidEmail(user) else 'username'
                    response = table.scan(
                        FilterExpression=Attr(key).eq(user)
                    )
                    if response['Count'] != 0:
                        if(response['Items'][0]['isVerified']==0):
                            return HttpResponseRedirect("/accounts/verifyotp/")
                        
                        if(isDoctor==1 and 'isDoctor' not in response['Items'][0]):
                            return HttpResponseRedirect("/accounts/login/")

                        return function(*args,**kwargs)
            return HttpResponseRedirect("/accounts/login/")
        return wrapper_function
    return is_authenticated

def is_authenticated_notverified(function):
    def wrapper_function(*args,**kwargs):
        if 'user' in args[0].session:
            user = args[0].session['user']
            table = db.Table('users')
            if(isValidEmail(user) or isvalidUserName(user)):
                key = 'email' if isValidEmail(user) else 'username'
                response = table.scan(
                    FilterExpression=Attr(key).eq(user)
                )
                if response['Count'] != 0:
                    if(response['Items'][0]['isVerified']==0):
                        return function(*args,**kwargs)

        return HttpResponseRedirect("/accounts/login/")
    return wrapper_function\


