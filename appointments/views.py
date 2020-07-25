from django.shortcuts import render, HttpResponse, redirect
from accounts.decorators import isDoctor
# from boto3.dynamodb.conditions import Attr
# import boto3
from mongodb.mongolib import Table
import numpy
from accounts.decorators import getEmail
from datetime import date
import calendar
import requests
from faker import Faker
import random

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def find_day(date):
    day, month, year = (int(i) for i in date.split(' '))
    dayNumber = calendar.weekday(year, month, day)
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return (days[dayNumber])

@isDoctor(1)
def doc_home(request):
    table = Table('slots')
    email = getEmail(request.session['session_key'])
    print(email)
    response = table.scan(FilterExpression={'doc_id':email}).values()
    items = response['Items']
    print(items)
    c = 1
    for item in items:
        item['num'] = c
        item['start_time'] = str(item['start_time'][0:2]) + ":" + str(item['start_time'][2:4])
        item['end_time'] = str(item['end_time'][0:2]) + ":" + str(item["end_time"][2:4])
        item['fees'] = str(item['fees'])
        c += 1
    return render(request, "appointments/doc_slots.html", {'items':items})

# str(u"\u20B9") +

@isDoctor(1)
def add_slots(request):
    table = Table('slots')
    email = getEmail(request.session['session_key'])
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


    if request.method == 'POST':
        st_time = request.POST['st_time']
        end_time = request.POST['end_time']
        fees = request.POST['fees']
        dow = []
        for d in days:
            string = 'weekday-' + d
            if string in request.POST.keys():
                dow.append(d)
        data = table.scan(FilterExpression={}).values()
        items = data['Items']
        num = 0
        for it in items:
            c = int(it['slot_id'])
            if (c>num):
                num = c
        num += 1
        num = str(num)
        table.insertValues(values=[{
            'slot_id': num,
            'doc_id': email,
            'start_time': st_time,
            'end_time': end_time,
            'fees': fees,
            'days':dow }])
        print(table.scan(FilterExpression={'doc_id':email}).values())
    response = redirect('/appointments/doc_slots/')
    return response

@isDoctor(1)
def del_slots(request):
    table = Table('slots')
    email = getEmail(request.session['session_key'])

    list = []
    if request.method == 'POST':
        # print(request.POST)
        for key, val in request.POST.items():
            if val == 'on':
                list.append(key)
    print(list)
    for id in list:
        table.delete(FilterExpression={
                'slot_id':id
            })
    response = redirect('/appointments/')
    return response

@isDoctor(1)
def check_appointments(request):
    table = Table('appointments')
    email = getEmail(request.session['session_key'])
    response = table.scan(FilterExpression={'doc_id':email}).values()
    items = response['Items']
    c = 1
    for item in items:
        item['num'] = c
        item['start_time'] = str(item['start_time'][0:2]) + ":" + str(item['start_time'][2:4])
        item['end_time'] = str(item['end_time'][0:2]) + ":" + str(item["end_time"][2:4])
        item['fees'] = str(item['fees'])
        c += 1
    return render(request, "appointments/doc_appoints.html", {'items':items})

@isDoctor(1)
def cancel_appointments(request):
    table = Table('appointments')

    list = []
    if request.method == 'POST':
        # print(request.POST)
        for key, val in request.POST.items():
            if val == 'on':
                list.append(key)
    print(list)
    for id in list:
        table.delete(FilterExpression={
                'app_id':id
            })
    response = redirect('/appointments/check_app/')
    return response


# @isDoctor(0)
def check_avail(request):
    if request.method == "POST":
        table = Table('slots')
        city = request.POST['city_name']
        locality = request.POST['locality']
        spec = request.POST['spec']
        date = request.POST['date_app']

        info = table.scan(FilterExpression={'spec':spec}).sort("start_time")
        doc_info = info['Items']
        print(info)
        return render(request, "appointments/pat_book.html", {'doc_info':doc_info})
    else:
        return render(request, "appointments/pat_slots.html")

# @isDoctor(0)
def appoint(request):
    table = Table('appointments')
    table2 = Table('slots')
    data = table.scan(FilterExpression={}).values()
    # email = getEmail(request.session['session_key'])
    # print(data)
    # print(request.POST['slot_id'])
    email = "lushaank@gmail.com"
    if request.method == "POST":
        num = 0
        items = data['Items']
        for it in items:
            c = int(it['app_id'])
            if (c>num):
                num = c
        num += 1
        # print(num)
        d = table2.scan(FilterExpression={'slot_id':request.POST['slot_id']}).values()
        for it in d['Items']:
            print(it)
            doc_id = it['doc_id']
            spec = it['spec']
            start_time = it['start_time']
            end_time = it['end_time']
            fees = it['fees']
        d1 = table.scan(FilterExpression={'doc_id':doc_id, 'spec':spec, 'pat_id':email, 'start_time':start_time, 'end_time':end_time}).values()
        if d1['Count'] == 0:
            table.insertValues(values=[{
                    'app_id': str(num),
                    'doc_id': doc_id,
                    'spec': spec,
                    'pat_id':email,
                    'start_time': start_time,
                    'end_time': end_time,
                    'fees': fees,
                    'date':'30072020' }])
            # return render(request, "p/", {'app_id':str(num)})
            return HttpResponse("Appointment Added")
        else:
            for item in d1['Items']:
                sst = int(start_time)
                snt = int(end_time)
                ist = int(item['start_time'])
                iet = int(item['end_time'])
                if ist < sst < iet:
                    return HttpResponse("New appointment can't be created due to clashing of appointment times")
                elif ist < snt < iet:
                    return HttpResponse("New appointment can't be created due to clashing of appointment times")
                elif (sst == ist) & (snt == iet):
                    return HttpResponse("New appointment can't be created due to clashing of appointment times")
                else:
                    table.insertValues(values=[{
                        'app_id': str(num),
                        'doc_id': doc_id,
                        'spec': spec,
                        'pat_id':email,
                        'start_time': start_time,
                        'end_time': end_time,
                        'fees': fees,
                        'date':'30072020' }])
                    return HttpResponse("Appointment Added")


def create_doc(request):
    table = Table('slots')
    table.delete()
    fake = Faker()
    for i in range(1,1001):
        doc = fake.email()
        lat = str(fake.latitude())
        lon = str(fake.longitude())
        fees = random.randint(100, 1000)
        special = ['Allergists', 'Anesthesiologists', 'Cardiologists', 'Dermatologists', 'Endocrinologists',
        'FamilyPhysicians', 'Gastroenterologists', 'Hematologists', 'InfectiousDiseaseSpecialists', 'Internists',
        'MedicalGeneticists', 'Nephrologists', 'Neurologists', 'Obstetricians', 'Gynecologists',
        'Oncologists', 'Ophthalmologists', 'Osteopaths', 'Otolaryngologists', 'Pathologists',
        'Pediatricians', 'Physiatrists', 'PlasticSurgeons', 'Podiatrists', 'PreventiveMedicineSpecialists',
        'Psychiatrists', 'Pulmonologists', 'Radiologists', 'Rheumatologists', 'GeneralSurgeons', 'Urologists']
        s_rand = random.randint(0, 30)
        spec = special[s_rand]
        th1 = random.randint(0,23)
        th2 = (th1+2)%24
        t1 = str(th1) + "00"
        t2 = str(th2) + "00"
        dow = ['mon', 'tue', 'wed', 'thu', 'fri']
        r = random.random()
        if r>=0.8:
            dow.append('sat')
        if r>=0.9:
            dow.append('sun')
        table.insertValues(values=[{
                'slot_id': str(i),
                'doc_id': doc,
                'spec': spec,
                'start_time': t1,
                'end_time': t2,
                'fees': fees,
                # 'days': dow,
                'lon': lon,
                'lat': lat}])
    return HttpResponse("You have generated data")
@isDoctor(1)
def dashboard(request):
    email = getEmail(request.session['session_key'])
    date = str(date.today())
    today = date[8:10]+date[5:7]+date[0:4]
    table = Table('appointments')
    result = table.scan(FilterExpression={'date':today,'doc_id':email}).values()
    return render(request,'appointments/dashboard.html',{'app' : result['Items']})
