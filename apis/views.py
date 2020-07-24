from rest_framework.decorators import api_view
from rest_framework.response import Response
from doca.settings import SECRET_KEY, SECRET_KEY2
import hashlib
from datetime import datetime, timedelta
from accounts.verifylib import isValidEmail, isvalidPassword, isvalidUserName
from accounts.forms import SignupForm
from mongodb.mongolib import Table
import jwt



register_secret_key = "fvfnh654x#R&^yhvbv@E%#(*gcgf51$@EfdgdhE#^@Rgdhfgdred"


@api_view(['POST'])
def getTokenPair(request):
    print(request.POST)
    if 'user' in request.POST and 'password' in request.POST:
        user = request.POST['user']
        password = request.POST['password']
        table = Table("users")
        if(isValidEmail(user) and isvalidPassword(password)):
            password = hashlib.sha256((password+SECRET_KEY).encode())
            password = password.hexdigest()
            response = table.scan(FilterExpression={'email':user}).values() 
            if response['Count'] == 0:
                return Response({
                    "code": "1",
                    "message": "Incorrect Username/email address or password"
                })

            password0 = response['Items'][0]['password']
            if (password == password0):
                if response['Items'][0]['isVerified'] == 0:
                    return Response({"code": "2",
                                     "message": "please verify your email id first",
                                     })
                isDoctor = 1 if 'isDoctor' in response['Items'][0] else 0
                if isDoctor == 0 :
                    primary_token = jwt.encode({"email": user,
                                                "timestamp": (datetime.now()+timedelta(minutes=15)).strftime("%Y%m%d%H%M%S"),
                                                }, SECRET_KEY2, algorithm="HS256")
                    refresh_token = jwt.encode({"email": user,
                                                "timestamp": (datetime.now()+timedelta(days=7)).strftime("%Y%m%d%H%M%S"),
                                                }, SECRET_KEY, algorithm="HS256")

                    return Response({
                        "code": "0",
                        "refresh_token": refresh_token,
                        "primary_token": primary_token,
                    })

        elif(isvalidUserName(user) and isvalidPassword(password)):
            password = hashlib.sha256((password+SECRET_KEY).encode())
            password = password.hexdigest()
            response = table.scan(
                FilterExpression={'username':user}
            ).values()
            if response['Count'] == 0:
                return Response({
                    "code": "1",
                    "message": "Incorrect Username/email address or password"
                })
            user = response['Items'][0]['email']
            password0 = response['Items'][0]['password']
            if (password == password0):
                if response['Items'][0]['isVerified'] == 0:
                    return Response({"code": "2",
                                     "message": "please verify your email id first",
                                     })
                isDoctor = 1 if 'isDoctor' in response['Items'][0] else 0
                if isDoctor == 0:
                    primary_token = jwt.encode({"email": user,
                                                "timestamp": (datetime.now()+timedelta(minutes=15)).strftime("%Y%m%d%H%M%S"),
                                                }, SECRET_KEY2, algorithm="HS256")
                    refresh_token = jwt.encode({"email": user,
                                                "timestamp": (datetime.now()+timedelta(days=7)).strftime("%Y%m%d%H%M%S"),
                                                }, SECRET_KEY, algorithm="HS256")

                    return Response({
                        "code": "0",
                        "refresh_token": refresh_token,
                        "primary_token": primary_token,
                    })

    return Response({
        "code": "1",
        "message": "Incorrect Username/email address or password"
    })


@api_view(["POST"])
def getPrimaryToken(request):
    
    if 'token' in request.POST:
        token = request.POST['token']
        try:
            payload = jwt.decode(token.encode('utf-8'), SECRET_KEY, algorithms=['HS256'])
            
        except jwt.exceptions.DecodeError:
            
            return Response({
                "code": "1",
            }),

        email = payload['email']
        timestamp = payload['timestamp']
        print(timestamp)
        if datetime.strptime(timestamp, "%Y%m%d%H%M%S") < datetime.now():
            return Response({
                "code": "2",
            }),
        if isValidEmail(email):
            refresh_token = jwt.encode({"email": email,
                                        "timestamp": (datetime.now()+timedelta(days=7)).strftime("%Y%m%d%H%M%S"),
                                        }, SECRET_KEY, algorithm="HS256")

            return Response({"code": "0",
                             "primary_token": refresh_token,
                             })
            
    return Response({"code":"0"})

def is_authenticated(request):
    if 'HTTP_TOKEN' in request.META:
        http_token = (request.META['HTTP_TOKEN'])
        try:
            payload = jwt.decode(http_token.encode(
                'utf-8'), SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.DecodeError:
            return 0
        username = payload['username']
        mTimestamp = datetime.strptime(payload['timestamp'], "%Y%m%d%H%M%S")
        if datetime.now() < mTimestamp:
            return username

    return 0


@api_view(['POST'])
def register(request):
    print(request.POST)
    if 'username' in request.POST and 'email' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        table = Table('users')
        if(isvalidPassword(password) and isvalidUserName(username) and isValidEmail(email)):
            password = hashlib.sha256((password+SECRET_KEY).encode())
            password = password.hexdigest()
            """table.put_item(Item={
                'email': email,
                'password': password,
                'username': username,
                'isVerified': 0,
            })"""

            register_token = jwt.encode({
                'email': email,
                'timestamp': (datetime.now()+timedelta(minutes=15)).strftime("%Y%d%M%H%M%S"),
            }, register_secret_key, algorithm='HS256')

            return Response({
                "code": "0",
                "register_token":register_token,
            })

        emailerr = usernameerr = passworderr = ""
        if (isValidEmail(email) == False):
            emailerr = "Invalid email address"
        if (isvalidPassword(password) == False):
            passworderr = "Invalid Password"
        if (isvalidUserName(username) == False):
                usernameerr = "Invalid UserName"
            

        return Response({
                    "code": "1",
                    "err":emailerr+"\n"+passworderr+"\n"+usernameerr,
                })
    return Response({
                    "code": "2",
                    "err":"Invalid request",
                })
    
    
@api_view(['GET'])
def getSpecialization(request):
    if 'spec' in request.GET:
        table = Table('Specilizations')
        spec0 =  request.GET['spec']
        specs = table.scan().values()['Items']
        res = []
        for spec1 in specs:
            if spec0.lower() in spec1['spec'].lower():
                res.append(
                    spec1['spec'],
                )
        return Response({
            "code":0,
            "results":res,
        })
    return Response({"code":"404","message":"invalid request"})

@api_view(['GET'])
def getCities(request):
    if 'city' in request.GET:
        table = Table('Cities')
        spec0 =  request.GET['city']
        specs = table.scan().sort("city_id")['Items']
        res = []
        for spec1 in specs:
            if spec0.lower() in spec1['city'].lower():
                res.append(
                    {"city":spec1['city'],"state":spec1['state']}
                )
        return Response({
            "code":0,
            "results":res,
        })
    return Response({"code":"404","message":"invalid request"})
    
    
    