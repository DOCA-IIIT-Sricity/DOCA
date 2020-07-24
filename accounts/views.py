from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm,SignupForm,OTPVerificationForm,FindAccountForm,ChangePasswordForm,ApplyForm
from .verifylib import isValidEmail,isvalidPassword,isvalidUserName
from .decorators import is_authenticated_notverified,is_not_authenticated,isDoctor,getEmail
from doca.settings import SECRET_KEY
from datetime import datetime,timedelta
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import random
import jwt
import hashlib
from mongodb.mongolib import Table

@is_not_authenticated
def apply(request):
    if request.method == "GET":
        return render(request,'accounts/applyasdoctor.html')
    if request.method == "POST":
        if 'fname' in request.POST and 'lname' in request.POST and 'email' in request.POST and 'city' in request.POST and 'spec' in request.POST and 'address' in request.POST:
            form=ApplyForm(request.POST)

            if True:
                print("valid form")
                fname = request.POST['fname']
                lname = request.POST['lname']
                password = request.POST['password']
                email = request.POST['email']
                city = request.POST['city']
                spec = request.POST['spec']
                address = request.POST['address']
                table = Table('users')
                if(isvalidPassword(password) and isValidEmail(email)):
                    password=hashlib.sha256((password+SECRET_KEY).encode())
                    password=password.hexdigest()

                    username = fname + lname

                    table.insertValues(values=[{
                        'email':email,
                        'password':password,
                        'username':username,
                        'isVerified':0,
                        'isDoctor': 1,
                    }])

                    table = Table('doctor')
                    table.insertValues(values=[{
                        "doc_id":email,
                        "first_name":fname,
                        "last_name":lname,
                        "city":city,
                        "address":address,
                        "spec":spec,
                    }])

                    table = Table('SessionStore')

                    tkey = email + datetime.now().strftime("%Y%m%d%H%M%S") + SECRET_KEY
                    tkey = str(hashlib.sha256(tkey.encode()).hexdigest())
                    table.insertValues(values=[{
                        "session_key":tkey,
                        "email":email,
                        "timestamp":datetime.now().strftime("%Y%m%d%H%M%S"),
                        "isVerified" : 0 ,
                        "isDoctor": 1,
                    }])
                    request.session['session_key'] = tkey;

                    return HttpResponseRedirect("/accounts/verifyotp/")

            print("form invalid")
        return render(request,'accounts/applyasdoctor.html')


def sendOtp(to,val1):
    otp_gen=random.randint(100000,999999)
    otp = hashlib.sha256((str(otp_gen)+SECRET_KEY).encode()).hexdigest()
    subject = 'Your otp for DOCA registration  is '+str(otp_gen)
    message = ' it  means a world to us thanks for choosing us \n your otp is : '+str(otp_gen)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to,]
    message = EmailMultiAlternatives(subject = subject, body =message,from_email=email_from ,to = recipient_list)
    htmlTemplate = render_to_string('accounts/email_template/sign_up.html', {'otp': otp_gen})
    message.attach_alternative(htmlTemplate,'text/html')
    response = message.send()
    if response == 1 :
        table = Table('otp')
        table.insertValues(values=[{
            'otp' : otp,
            'email': to,
            'isRegister' : val1,
            'timestamp' : str(datetime.now().strftime("%Y%m%d%H%M%S"))
        }] )
    return response


def sendLink(to,val1):
    subject = 'Reset Password Link'
    message = ' to reset your password click below link: http://127.0.0.1:8000/accounts/changepassword/?tk='+val1
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to,]
    message = EmailMultiAlternatives(subject = subject, body =message,from_email=email_from ,to = recipient_list)
    htmlTemplate = render_to_string('accounts/email_template/forgot.html', {'link': 'http://127.0.0.1:8000/accounts/changepassword/?tk='+val1 })
    message.attach_alternative(htmlTemplate,'text/html')
    response = message.send()
    print(response)
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
            table = Table('users')
            if(isValidEmail(user) and isvalidPassword(password)):
                password=hashlib.sha256((password+SECRET_KEY).encode())
                password=password.hexdigest()
                response = table.scan(FilterExpression={'email':user}).values()

                if response['Count']==0:
                    return render(request,'accounts/login.html',{"err":"Invalid Email address/UserName or Password","user":user})

                password0 = response['Items'][0]['password']
                if (password == password0):
                    table = Table('SessionStore')
                    tkey = response['Items'][0]['email'] + datetime.now().strftime("%Y%m%d%H%M%S") + SECRET_KEY
                    tkey = str(hashlib.sha256(tkey.encode()).hexdigest())
                    table.insertValues(values=[{
                        "session_key": tkey,
                        "email":response['Items'][0]['email'],
                        "timestamp":datetime.now().strftime("%Y%m%d%H%M%S"),
                        "isVerified":response['Items'][0]['isVerified'],
                        "isDoctor": 1 if 'isDoctor' in response['Items'][0] else 0,
                    }])
                    request.session['session_key'] = tkey;

                    if response['Items'][0]['isVerified'] == 0 :
                        return HttpResponseRedirect('/accounts/verifyotp/')

                    if 'isDoctor' not in response['Items'][0] :
                        return HttpResponse("<H1> Patient HomePage </H1>")
                    return render(request,'appointments/dashboard')

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
            table = Table('users')
            if(isvalidPassword(password) and isvalidUserName(username) and isValidEmail(email)):
                password=hashlib.sha256((password+SECRET_KEY).encode())
                password=password.hexdigest()

                table.insertValues(values=[{
                    'email':email,
                    'password':password,
                    'username':username,
                    'isVerified':0,
                }])

                table = Table('SessionStore')

                tkey = email + datetime.now().strftime("%Y%m%d%H%M%S") + SECRET_KEY
                tkey = str(hashlib.sha256(tkey.encode()).hexdigest())
                table.insertValues(values=[{
                    "session_key":tkey,
                    "email":email,
                    "timestamp":datetime.now().strftime("%Y%m%d%H%M%S"),
                    "isVerified" : 0 ,
                    "isDoctor": 0,
                }])
                request.session['session_key'] = tkey;

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
    email = getEmail(request.session['session_key'])
    if request.method == "GET":
        table = Table('otp')
        response = table.scan(
            FilterExpression={'email': email}
        ).values()

        if response['Count'] == 0:
            sendOtp(email,1)

        else:
            for x in response['Items']:
                date_time = datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S")
                is4verify = 1 if 'isRegister' in x else 0
                if datetime.now() > date_time + timedelta(minutes=15):
                    sendOtp(email,1)
                    table.delete(
                        FilterExpression = {
                            'otp' : x['otp']
                        }
                    )
                    break
                if is4verify == 0 :
                    sendOtp(email,1)
        return render(request,'accounts/verification.html')

    if request.method == "POST" :
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            generatedotp = form.cleaned_data['o1']+form.cleaned_data['o2']+form.cleaned_data['o3']+form.cleaned_data['o4']+form.cleaned_data['o5']+form.cleaned_data['o6']
            generatedotp = hashlib.sha256((generatedotp+SECRET_KEY).encode()).hexdigest()
            table = Table('otp')
            response = table.scan(
                    FilterExpression={'otp': generatedotp}
            ).values()

            if response['Count']==1:
                if response['Items'][0]['otp'] == generatedotp :
                    table.delete(
                        FilterExpression = {
                            'otp' : generatedotp,
                        }
                    )

                    table0 = Table('users')
                    print("has Updated")
                    table0.update(
                        FilterExpression={
                            'email' : email,
                        },
                        UpdateExpression={"isVerified" : 1 ,},
                    )
                    del request.session['session_key']
                    return HttpResponseRedirect('/accounts/login/')
                return render(request, 'accounts/verification.html',{'err':'OTP not match'})
            return HttpResponseRedirect('/accounts/login/')


#

@is_not_authenticated
def forgot(request):
    if request.method == "GET":
        return render(request,'accounts/forgot_password.html')
    if request.method == "POST":
        form = FindAccountForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            table = Table('users')
            if(isValidEmail(user)):
                response = table.scan(
                    FilterExpression={'email':user}
                ).values()

                if response['Count'] == 1:
                    timestamp0 = datetime.now().strftime('%Y%m%d%H%M%S')
                    signature = hashlib.sha256((user + timestamp0 + SECRET_KEY).encode()).hexdigest()
                    table = Table('forgototpsignatures')
                    table.insertValues(values=[{
                        'signature':signature,
                    }])

                    tk = jwt.encode({'email':user,'timestamp':timestamp0,'signature':signature},SECRET_KEY,algorithm='HS256')
                    tk = tk.decode('utf8')
                    sendLink(user,tk)
                    return HttpResponse("We have sent link to your email check it")
                return render(request,'accounts/forgot_password.html',{'err':'Account not found'})
            return render(request,'accounts/forgot_password.html',{'err':'Invalid Email Address'})
        return render(request,'accounts/forgot_password.html',{'err':'Something went wrong'})





@isDoctor(0)
def logout(request):
    if 'session_key' in request.session:
        table = Table('SessionStore')
        table.delete(FilterExpression={'session_key':request.session['session_key']})
        del request.session['session_key']
    return HttpResponse("LOGED OUT")

@isDoctor(1)
def logoutD(request):
    if 'session_key' in request.session:
        table = Table('SessionStore')
        table.delete(FilterExpression={'session_key':request.session['session_key']})
        del request.session['session_key']
    return HttpResponse("LOGED OUT")
#HttpResponseRedirect('/accounts/login/')

def changePassword(request):
    if request.method == "GET":
        if 'tk' in request.GET:
            tk = request.GET['tk']
            tk = tk.encode('utf-8')
            jdata = jwt.decode(tk,SECRET_KEY,algorithms=['HS256'])

            if 'timestamp' not in jdata or 'email' not in jdata or 'signature' not in jdata:
                return render(request,'global/400.html')

            if datetime.strptime(jdata['timestamp'],"%Y%m%d%H%M%S") + timedelta(minutes=5) < datetime.now():
                return render(request,'global/400.html')

            email = jdata['email']
            timestamp0 = jdata['timestamp']
            signature = jdata['signature']
            genSignature = hashlib.sha256((email+timestamp0+SECRET_KEY).encode()).hexdigest()
            if signature != genSignature :
                return render(request,'global/400.html')
            table = Table('forgototpsignatures')
            resp = table.scan(
                FilterExpression = {'signature':signature}
            ).values()

            if resp['Count'] != 1 :
                return render(request,'global/400.html')
            return render(request,'accounts/change_password.html',{'tk' : tk.decode('utf-8')})
        return render(request,'global/400.html')

    if request.method == "POST" :
        form = ChangePasswordForm(request.POST)
        err=""
        if form.is_valid():
            tk = form.cleaned_data['tk']
            paswd = form.cleaned_data['new_paswd']
            cpaswd = form.cleaned_data['cnfrm_paswd']
            if isvalidPassword(paswd) == False or isvalidPassword(cpaswd)==False:
                err+="password should contain one Capital letter on small letter and one Number"
            if cpaswd != paswd :
                err+="password not matched"

            if err=="":
                tk = tk.encode('utf-8')
                jdata = jwt.decode(tk,SECRET_KEY,algorithms=['HS256'])

                if 'timestamp' not in jdata or 'email' not in jdata or 'signature' not in jdata:
                    return render(request,'global/400.html')

                if datetime.strptime(jdata['timestamp'],"%Y%m%d%H%M%S") + timedelta(minutes=5) < datetime.now():
                    return render(request,'global/400.html')

                email = jdata['email']
                timestamp0 = jdata['timestamp']
                signature = jdata['signature']
                genSignature = hashlib.sha256((email+timestamp0+SECRET_KEY).encode()).hexdigest()
                if signature != genSignature :
                    return render(request,'global/400.html')
                table = Table('forgototpsignatures')
                resp = table.scan(
                    FilterExpression = {'signature':signature}
                ).values()
                if resp['Count'] != 1 :
                    return render(request,'global/400.html')
                table.delete(
                    FilterExpression = {'signature':signature}
                )
                hasedpassword= hashlib.sha256((paswd+SECRET_KEY).encode()).hexdigest()
                table = Table('users')
                table.update(
                    FilterExpression={'email':email},
                    UpdateExpression={'password':hasedpassword},
                )
                return HttpResponse("Password Changed Successfully")
            return render(request,'accounts/change_password.html',{'err':err,'tk':tk})
        return render(request,'accounts/change_password.html',{'err':err})

@isDoctor(0)
def uploadDp(request):
    email = getEmail(request.session['session_key'])
    if request.method == "GET":
        return render(request,'accounts/uploadPicture.html')


def sendDemoMail(request):
    sendOtp('dindisaikarthikk@gmail.com',0)
    return HttpResponse("SENT")
