from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm,SignupForm,OTPVerificationForm
import boto3
import hashlib
from .verifylib import isValidEmail,isvalidPassword,isvalidUserName
from boto3.dynamodb.conditions import Key, Attr
from .decorators import is_authenticated_notverified,is_not_authenticated,isDoctor
from doca.settings import SECRET_KEY
from datetime import datetime,timedelta
from django.core.mail import send_mail
from django.conf import settings
import random


db=boto3.resource('dynamodb')

def sendOtp(to):
    otp_gen=random.randint(100000,999999)
    otp = hashlib.sha256((str(otp_gen)+SECRET_KEY).encode()).hexdigest()
    subject = 'Your otp for the Fifa auction  is '+str(otp_gen)
    message = ' it  means a world to us thanks for choosing us \n your otp is : '+str(otp_gen)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to,]
    response=send_mail( subject, message, email_from, recipient_list,fail_silently=False)
    if response == 1 :
        table = db.Table('otp')
        table.put_item(Item={
            'otp' : otp,
            'email': to,
            'isRegister' : 1,
            'timestamp' : str(datetime.now().strftime("%Y%m%d%H%M%S"))
        } )
    return response


@is_not_authenticated
def login(request):
    if request.method == "GET" :
        return render(request,'accounts/login.html')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            table = db.Table('users')
            if(isValidEmail(user) and isvalidPassword(password)):
                password=hashlib.sha256((password+SECRET_KEY).encode())
                password=password.hexdigest()
                response = table.scan(
                    FilterExpression=Attr('email').eq(user)
                )
                if response['Count']==0:
                    print("LOL")
                    return render(request,'accounts/login.html',{"err":"Invalid Email address/UserName or Password","user":user})
                
                password0 = response['Items'][0]['password']
                if (password == password0):
                    
                    request.session['email']= response['Items'][0]['email']
                    request.session['valid']  = str(datetime.now().strftime("%Y%m%d%H%M%S"))
                    request.session['isVerified'] = int(response['Items'][0]['isVerified'])
                    isDoctor = response['Items'][0]['isDoctor'] if 'isDoctor' in response['Items'][0] else 0
                    request.session['isDoctor'] =isDoctor
                    tkey =request.session['email'] + str(isDoctor)+ request.session['valid'] + str(request.session['isVerified'] ) + SECRET_KEY
                    request.session['signature0']  = str(hashlib.sha256(tkey.encode()).hexdigest())
                    if response['Items'][0]['isVerified'] == 0 :
                        return HttpResponseRedirect('/accounts/verifyotp/')
                    if request.session['isDoctor'] == 0 :
                        return HttpResponse("<H1> Patient HomePage </H1>")
                    return HttpResponse("<H1> Doctor HomePage </H1>")
                    
                else:
                    return render(request,'accounts/login.html',{"err":"Invalid Email address/UserName or Password","userI":user})
            else :
                
                return render(request,'accounts/login.html',{"err":"Invalid Email address/UserName or Password"})

        return render(request,'accounts/login.html')



@is_not_authenticated
def signup(request):
    if request.method == "GET":
        return render(request,'accounts/signup.html')

    if request.method == "POST":
        form=SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            table = db.Table('users')
            if(isvalidPassword(password) and isvalidUserName(username) and isValidEmail(email)):
                password=hashlib.sha256((password+SECRET_KEY).encode())
                password=password.hexdigest()
                table.put_item(Item={
                    'email':email,
                    'password':password,
                    'username':username,
                    'isVerified':0,
                })
                return HttpResponseRedirect("/accounts/verifyotp/")
            emailerr = usernameerr = passworderr =""
            if (isValidEmail(email)==False):
                emailerr="Invalid email address"
            if (isvalidPassword(password)==False):
                passworderr="Invalid Password"
            if (isvalidUserName(username)==False):
                usernameerr="Invalid UserName"



            print(username+"\t"+password+"\t"+email)


        return render(request,'accounts/signup.html',{'err':emailerr+'\t'+passworderr+'\t'+usernameerr})


@is_authenticated_notverified
def verifyotp(request):
    if request.method == "GET":
        table = db.Table('otp')
        response = table.scan(
            FilterExpression=Attr('email').eq(request.session['email'])
        )
        if response['Count'] == 0:
            pass
            sendOtp(request.session['email'])
        else:
            for x in response['Items']:
                date_time = datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S")
                is4verify = 1 if 'isRegister' in x else 0
                if datetime.now() > date_time + timedelta(minutes=15):
                    sendOtp(request.session['email'])
                    table.delete_item(
                        Key = {
                            'otp' : x['otp']
                        }
                        #FilterExpression=Attr('otp').eq(x['otp'])
                    )
                    break
                if is4verify == 0 :
                    sendOtp(request.session['email'])

        return render(request,'accounts/verification.html')
    if request.method == "POST" :
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            generatedotp = form.cleaned_data['o1']+form.cleaned_data['o2']+form.cleaned_data['o3']+form.cleaned_data['o4']+form.cleaned_data['o5']+form.cleaned_data['o6']
            generatedotp = hashlib.sha256((generatedotp+SECRET_KEY).encode()).hexdigest()
            table = db.Table('otp')
            user = request.session['email']
            key = 'email'
            response = table.scan(
                    FilterExpression=Attr(key).eq(user)
            )
            if response['Count']==1:

                if response['Items'][0]['otp'] == generatedotp :
                    table.delete_item(
                        Key = {
                            'otp' : generatedotp,
                        }
                        #FilterExpression=Attr('otp').eq(generatedotp)
                    )
                    table0 = db.Table('users')
                    table0.update_item(
                        Key={
                            key : user,
                        },
                        UpdateExpression='SET isVerified = :val1',
                        ExpressionAttributeValues={
                            ':val1': 1
                        }
                    )
                    return HttpResponseRedirect('/accounts/login/')
                return render(request, 'accounts/verification.html',{'err':'OTP not match'})
            return HttpResponseRedirect('/accounts/login/')




@is_not_authenticated
def forgot(request):
    if request.method == "GET":
        return render(request,'accounts/forgot_password.html')


def logout(request):
    if 'email' in request.session:
        del request.session['email']
    if 'valid' in request.session:
        del request.session['valid']
    if 'isDoctor' in request.session:
        del request.session['isDoctor']
    if 'signatue' in request.session:
        del request.session['signature']
    return HttpResponse("LOGED OUT")#HttpResponseRedirect('/accounts/login/')

def changePassword(request):
    return render(request,'accounts/change_password.html')