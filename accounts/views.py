from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginForm,SignupForm,OTPVerificationForm,FindAccountForm,ChangePasswordForm
import boto3
import hashlib
from .verifylib import isValidEmail,isvalidPassword,isvalidUserName
from boto3.dynamodb.conditions import Key, Attr
from .decorators import is_authenticated_notverified,is_not_authenticated,isDoctor
from doca.settings import SECRET_KEY
from datetime import datetime,timedelta
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import random
import jwt


db=boto3.resource('dynamodb')

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
        table = db.Table('otp')
        table.put_item(Item={
            'otp' : otp,
            'email': to,
            'isRegister' : val1,
            'timestamp' : str(datetime.now().strftime("%Y%m%d%H%M%S"))
        } )
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
            table = db.Table('users')
            if(isValidEmail(user) and isvalidPassword(password)):
                password=hashlib.sha256((password+SECRET_KEY).encode())
                password=password.hexdigest()
                response = table.scan(
                    FilterExpression=Attr('email').eq(user)
                )
                if response['Count']==0:
                    return render(request,'accounts/login.html',{"err":"Invalid Email address/UserName or Password","user":user})
                
                password0 = response['Items'][0]['password']
                if (password == password0):
                    
                    request.session['email']= response['Items'][0]['email']
                    request.session['valid']  = str(datetime.now().strftime("%Y%m%d%H%M%S"))
                    request.session['isVerified'] = int(response['Items'][0]['isVerified'])
                    isDoctor = int(response['Items'][0]['isDoctor']) if 'isDoctor' in response['Items'][0] else 0
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
                request.session['email']=email
                request.session['valid']  = str(datetime.now().strftime("%Y%m%d%H%M%S"))
                request.session['isVerified'] = "0"
                isDoctor = "0"
                request.session['isDoctor'] =isDoctor
                tkey =request.session['email'] + str(isDoctor)+ request.session['valid'] + str(request.session['isVerified']) + SECRET_KEY
                request.session['signature0']  = str(hashlib.sha256(tkey.encode()).hexdigest())
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
            sendOtp(request.session['email'],1)
        else:
            for x in response['Items']:
                date_time = datetime.strptime(x['timestamp'], "%Y%m%d%H%M%S")
                is4verify = 1 if 'isRegister' in x else 0
                if datetime.now() > date_time + timedelta(minutes=15):
                    sendOtp(request.session['email'],1)
                    table.delete_item(
                        Key = {
                            'otp' : x['otp']
                        }
                        #FilterExpression=Attr('otp').eq(x['otp'])
                    )
                    break
                if is4verify == 0 :
                    sendOtp(request.session['email'],1)

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


#

@is_not_authenticated
def forgot(request):
    if request.method == "GET":
        return render(request,'accounts/forgot_password.html')
    if request.method == "POST":
        form = FindAccountForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            table = db.Table('users')
            if(isValidEmail(user)):
                response = table.scan(
                    FilterExpression=Attr('email').eq(user)
                )
                if response['Count'] == 1:
                    timestamp0 = datetime.now().strftime('%Y%m%d%H%M%S')
                    signature = hashlib.sha256((user + timestamp0 + SECRET_KEY).encode()).hexdigest()
                    table = db.Table('forgototpsignatures')
                    table.put_item(Item={
                        'signature':signature,
                    })

                    tk = jwt.encode({'email':user,'timestamp':timestamp0,'signature':signature},SECRET_KEY,algorithm='HS256')
                    tk = tk.decode('utf8')
                    sendLink(user,tk)
                    return HttpResponse("We have sent link to your email check it")
                return render(request,'accounts/forgot_password.html',{'err':'Account not found'})
            return render(request,'accounts/forgot_password.html',{'err':'Invalid Email Address'})
        return render(request,'accounts/forgot_password.html',{'err':'Something went wrong'})
        
                

        


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
            table = db.Table('forgototpsignatures')
            resp = table.scan(
                FilterExpression = Attr('signature').eq(signature) 
            )
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
                table = db.Table('forgototpsignatures')
                resp = table.scan(
                    FilterExpression = Attr('signature').eq(signature) 
                )
                if resp['Count'] != 1 :
                    return render(request,'global/400.html')
                table.delete_item(
                    Key={
                        'signature':signature,
                    }
                )
                hasedpassword= hashlib.sha256((paswd+SECRET_KEY).encode()).hexdigest()
                table = db.Table('users')
                table.update_item(
                    Key={
                            'email':email,
                        },
                    UpdateExpression='SET password = :val1',
                    ExpressionAttributeValues={
                        ':val1': hasedpassword
                    }
                )
                return HttpResponse("Password Changed Successfully")


            return render(request,'accounts/change_password.html',{'err':err,'tk':tk})
        return render(request,'accounts/change_password.html',{'err':err})

        
        

def sendDemoMail(request):
    sendOtp('dindisaikarthikk@gmail.com',0)
    return HttpResponse("SENT")
