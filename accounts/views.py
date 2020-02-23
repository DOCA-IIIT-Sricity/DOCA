from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm,SignupForm,OTPVerificationForm
import boto3
import hashlib
from .verifylib import isValidEmail,isvalidPassword,isvalidUserName
from boto3.dynamodb.conditions import Key, Attr
from .decorators import is_authenticated_notverified

db=boto3.resource('dynamodb')

def login(request):
    if request.method == "GET" :
        return render(request,'login.html')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            table = db.Table('users')
            if(isValidEmail(user) and isvalidPassword(password)):
                password=hashlib.sha256(password.encode())
                password=password.hexdigest()
                response = table.scan(
                    FilterExpression=Attr('email').eq(user)
                )
                password0 = response['Items'][0]['password']
                if (password == password0):
                    request.session['user']=user
                    return HttpResponse("<H1> LOGIN SUCESSFUL </H1>")
                else:
                    print("hello")
                    return render(request,'login.html',{"err":"Invalid Email address/UserName or Password","user":user})
            else :
                
                return render(request,'login.html',{"err":"Invalid Email address/UserName or Password"})

        return render(request,'login.html')




def signup(request):
    if request.method == "GET":
        return render(request,'signup.html')

    if request.method == "POST":
        form=SignupForm(request.POST)
        #emailerr="",passworderr="",usernameerr=""
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            table = db.Table('users')
            if(isvalidPassword(password) and isvalidUserName(username) and isValidEmail(email)):
                password=hashlib.sha256(password.encode())
                password=password.hexdigest()
                table.put_item(Item={
                    'email':email,
                    'password':password,
                    'username':username,
                    'isVerified':0,
                })
                return HttpResponseRedirect("https://www.google.com")
            if (isValidEmail(email)==False):
                emailerr="Invalid email address"
            if (isvalidPassword(password)==False):
                passworderr="Invalid Password"
            if (isvalidUserName(username)==False):
                username="Invalid UserName"



            print(username+"\t"+password+"\t"+email)


        return render(request,'signup.html',{'error':'something went wrong'})

@is_authenticated_notverified
def verifyotp(request):
    if request.method == "GET":
        return render(request,'verification.html')
    if request.method == "POST" :
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            generatedotp = form.cleaned_data['o1']+form.cleaned_data['o2']+form.cleaned_data['o3']+form.cleaned_data['o4']+form.cleaned_data['o5']+form.cleaned_data['o6']
            generatedotp = hashlib.sha256(generatedotp.encode())
            table = db.Table('otp')
            user = request.session['user']
            key = 'email' if isValidEmail(user) else 'username'
            response = table.scan(
                    FilterExpression=Attr(key).eq(user)
            )
            if response['Count']==1:
                if response['Items'][0]['otp'] == generatedotp :
                    table0 = db.Table('user')
                    table.update_item(
                        Key={
                            key : user,
                        },
                        UpdateExpression='SET isVerified = :val1',
                        ExpressionAttributeValues={
                            ':val1': 1
                        }
                    )
                    return HttpResponseRedirect('/acounts/login/')
                return render(request, 'verification.html',{'err':'OTP not match'})
            return HttpResponseRedirect('/accounts/login/')





def forgot(request):
    if request.method == "GET":
        return render(request,'forgot_password.html')


