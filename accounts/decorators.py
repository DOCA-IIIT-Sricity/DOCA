from django.http import HttpResponseRedirect
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
                gensignature = hashlib.sha256((email+isDoctor0+valid+SECRET_KEY).encode).hexdigest()
                if (gensignature == signature and isDoctor == isDoctor0):
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


