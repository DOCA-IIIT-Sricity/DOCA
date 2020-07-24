from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    user = forms.CharField() 
    password = forms.CharField(widget=forms.PasswordInput)

class FindAccountForm(forms.Form):
    user = forms.CharField()

class ChangePasswordForm(forms.Form):
    tk = forms.CharField()
    new_paswd= forms.CharField(max_length=25)
    cnfrm_paswd= forms.CharField(max_length=25)

class SignupForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField()
    
class ApplyForm(forms.Form):
    fname = forms.CharField()
    lname = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField()
    spec = forms.CharField()
    phone = forms.CharField()
    city = forms.CharField()
    address = forms.CharField()

class OTPVerificationForm(forms.Form):
    o1 = forms.CharField(max_length=1)
    o2 = forms.CharField(max_length=1)
    o3 = forms.CharField(max_length=1)
    o4 = forms.CharField(max_length=1)
    o5 = forms.CharField(max_length=1)
    o6 = forms.CharField(max_length=1)

