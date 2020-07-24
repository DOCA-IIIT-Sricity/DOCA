from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import JsonResponse
from doca.settings import SECRET_KEY, SECRET_KEY2
import hashlib
from datetime import datetime, timedelta
from accounts.verifylib import isValidEmail, isvalidPassword, isvalidUserName
from accounts.forms import SignupForm
from mongodb.mongolib import Table
import jwt
import json
from django.shortcuts import HttpResponse

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
    
    
    

@api_view(['GET', 'POST'])
def slots_list(request):
    if is_authenticated != 0:
        table = Table('slots')
        res = table.scan(FilterExpression={}).values()
        if request.method == "GET":
            for i in res['Items']:
                i['_id'] = str(i['_id'])
            return Response(res)

        elif request.method == 'POST':
            slots_data = request.data
            # print(slots_data)
            if slots_data['method'] == "get_slots":
                res = table.scan(FilterExpression={'spec':slots_data['spec']}).values()
                for i in res['Items']:
                    i['_id'] = str(i['_id'])
                return Response(res)

            elif slots_data['method'] == "add_slots":
                d1 = table.scan(FilterExpression={'doc_id':slots_data['doc_id'], 'spec':slots_data['spec'], 'lon':slots_data['lon'], 'lat':slots_data['lat']}).values()
                if d1['Count'] == 0:
                    l = slots_data['doc_id']
                    sid = 0
                    for i in res['Items']:
                        if int(i['slot_id'][l:]) > sid:
                            sid = i['slot_id'][l:]
                    sid = int(sid) + 1
                    table.insertValues(values=[{
                            'slot_id': slots_data['doc_id'] + str(sid),
                            'doc_id': slots_data['doc_id'],
                            'spec' :slots_data['spec'],
                            'start_time': slots_data['start_time'],
                            'end_time': slots_data['end_time'],
                            'fees': slots_data['fees'],
                            'days':slots_data['days'],
                            'lon': slots_data['lon'],
                            'lat': slots_data['lat']}])
                    return HttpResponse("Added new value")
                else:
                    for item in d1['Items']:
                        sst = int(slots_data['start_time'])
                        snt = int(slots_data['end_time'])
                        ist = int(item['start_time'])
                        iet = int(item['end_time'])
                        if ist < sst < iet:
                            return HttpResponse("New slot can't be created due to clashing of slot times")
                        elif ist < snt < iet:
                            return HttpResponse("New slot can't be created due to clashing of slot times")
                        elif (sst == ist) & (snt == iet):
                            return HttpResponse("New slot can't be created due to clashing of slot times")
                        else:
                            l = slots_data['doc_id']
                            sid = 0
                            for i in res['Items']:
                                if int(i['slot_id'][l:]) > sid:
                                    sid = i['slot_id'][l:]
                            sid = int(sid) + 1
                            table.insertValues(values=[{
                                    'slot_id': slots_data['doc_id'] + str(sid),
                                    'doc_id': slots_data['doc_id'],
                                    'spec' :slots_data['spec'],
                                    'start_time': slots_data['start_time'],
                                    'end_time': slots_data['end_time'],
                                    'fees': slots_data['fees'],
                                    'days':slots_data['days'],
                                    'lon': slots_data['lon'],
                                    'lat': slots_data['lat']}])
                            return HttpResponse("Added new value")

            
            elif slots_data['method'] == "delete_slots":
                table.delete(FilterExpression={'slot_id':slots_data['slot_id']})
                return HttpResponse("Deleted that slot id")


@api_view(['GET', 'POST'])
def appoint_list(request):
    if is_authenticated != 0:
        table = Table('appointments')
        res = table.scan(FilterExpression={}).values()
        if request.method == "GET":
            for i in res['Items']:
                i['_id'] = str(i['_id'])
            return Response(res)
            
        elif request.method == 'POST':
            appoint_data = request.data
            if appoint_data['method'] == 'get_appointments':
                res = table.scan(FilterExpression={'doc_id':appoint_data['doc_id']}).values()
                for i in res['Items']:
                    i['_id'] = str(i['_id'])
                return Response(res)    
            elif appoint_data['method'] == 'add_appointments':
                for id in res['Items']:
                    # print(id, type(id))
                    aid = id['app_id']
                aid = int(aid) + 1
                table.insertValues(values=[{
                        'app_id': str(aid),
                        'doc_id': appoint_data['doc_id'],
                        'spec' :appoint_data['spec'],
                        'pat_id':appoint_data['pat_id'],
                        'start_time': appoint_data['start_time'],
                        'end_time': appoint_data['end_time'],
                        'fees': appoint_data['fees'],
                        'date':appoint_data['date']}])
                return HttpResponse("Added Appointments")
            elif appoint_data['method'] == 'delete_appointments':
                table.delete(FilterExpression={'app_id':appoint_data['app_id']})
                return HttpResponse("Deleted that slot id")

@api_view(['GET', 'POST'])
def med_list(request):
    if is_authenticated != 0:
        table = Table('med')
        res = table.scan(FilterExpression={}).values()
        if request.method == "GET":
            for i in res['Items']:
                i['_id'] = str(i['_id'])
            return Response(res)
            
        elif request.method == 'POST':
            med_data = request.data
            if med_data['method'] == 'get_medications':
                res = table.scan(FilterExpression={'med_id':med_data['med_id']}).values()
                for i in res['Items']:
                    i['_id'] = str(i['_id'])
                return Response(res)    
            elif med_data['method'] == 'add_medications':
                for id in res['Items']:
                    # print(id, type(id))
                    mid = id['med_id']
                mid = int(mid) + 1
                table.insertValues(values=[{
                        'med_id': str(mid),
                        'med': med_data['med']}])
                return HttpResponse("Added Medicines")
            elif med_data['method'] == 'delete_medcations':
                table.delete(FilterExpression={'med_id':med_data['med_id']})
                return HttpResponse("Deleted that slot id")

@api_view(['GET', 'POST'])
def symp_list(request):
    if is_authenticated != 0:
        table = Table('symp')
        res = table.scan(FilterExpression={}).values()
        if request.method == "GET":
            for i in res['Items']:
                i['_id'] = str(i['_id'])
            return Response(res)
            
        elif request.method == 'POST':
            symp_data = request.data
            if symp_data['method'] == 'get_symptoms':
                res = table.scan(FilterExpression={'symp_id':symp_data['symp_id']}).values()
                for i in res['Items']:
                    i['_id'] = str(i['_id'])
                return Response(res)    
            elif symp_data['method'] == 'add_symptoms':
                for id in res['Items']:
                    # print(id, type(id))
                    sid = id['symp_id']
                sid = int(sid) + 1
                table.insertValues(values=[{
                        'symp_id': str(sid),
                        'symp': symp_data['symp']}])
                return HttpResponse("Added Symptoms")
            elif symp_data['method'] == 'delete_symptoms':
                table.delete(FilterExpression={'symp_id':symp_data['symp_id']})
                return HttpResponse("Deleted that slot id")

@api_view(['GET', 'POST'])
def pres_table_list(request):
    if is_authenticated != 0:
        table = Table('pres_table')
        res = table.scan(FilterExpression={}).values()
        if request.method == "GET":
            for i in res['Items']:
                i['_id'] = str(i['_id'])
            return Response(res)
            
        elif request.method == 'POST':
            pres_table_data = request.data
            if pres_table_data['method'] == 'get_prescriptions':
                res = table.scan(FilterExpression={'app_id':pres_table_data['app_id']}).values()
                for i in res['Items']:
                    i['_id'] = str(i['_id'])
                return Response(res)    
            elif pres_table_data['method'] == 'add_prescriptions':
                for id in res['Items']:
                    # print(id, type(id))
                    pid = id['app_id']
                pid = int(pid) + 1
                table.insertValues(values=[{
                        'app_id': str(pid),
                        'doc_id': pres_table_data['doc_id'],
                        'pat_id':pres_table_data['pat_id'],
                        'symptoms': pres_table_data['symptoms'],
                        'notes': pres_table_data['notes'],
                        'tabs': pres_table_data['tabs']}])
                return HttpResponse("Added prescription")
            elif pres_table_data['method'] == 'delete_prescriptions':
                table.delete(FilterExpression={'app_id':pres_table_data['app_id']})
                return HttpResponse("Deleted that slot id")
