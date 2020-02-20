from django import forms 
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField() 
    password = forms.CharField(widget=forms.PasswordInput)

   

class SignupForm(forms.Form):
    username = forms.CharField() 
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField()
    

    
