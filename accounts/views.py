from django.shortcuts import render
from .forms import LoginForm,SignupForm
import boto3
import hashlib

db=boto3.resource('dynamodb') 

def login(request):
    if request.method == "GET" :
        return render(request,'login.html')

def signup(request):
    if request.method == "GET":
        return render(request,'signup.html')
    
    if request.method == "POST":
        form=SignupForm(request.POST)
        if form.is_valid():
            
            
        return render(request,'signup.html',{'error':'something went wrong'})
        
def verifyotp(request):
    if request.GET == "GET":
        return render(request,'verification.html')



