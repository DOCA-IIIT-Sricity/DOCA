from django.shortcuts import render
from django.http import HttpResponse
from .forms import LoginForm,SignupForm
import boto3
import hashlib
import re
from boto3.dynamodb.conditions import Key, Attr

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

def verifyotp(request):
    if request.method == "GET":
        return render(request,'verification.html')

def forgot(request):
    if request.method == "GET":
        return render(request,'forgot_password.html')

def isvalidUserName(username):
    if len(username) < 6 or len(username)>25:
        return False
    return True


def isvalidPassword(password):
    if len(password) < 8 or len(password)>25:
        return False
    if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',password))==True):
        return False
    return True
def isValidEmail(email):
    return re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',email)
