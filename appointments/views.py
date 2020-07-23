from django.shortcuts import render, HttpResponse, redirect
from accounts.decorators import isDoctor
# from boto3.dynamodb.conditions import Attr
# import boto3
from mongodb.mongolib import Table
import numpy
from accounts.decorators import getEmail
import datetime
import calendar
import requests
from faker import Faker 
import random

# Create your views here.
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
        time = request.POST['time']
        fees = request.POST['fees']
        dow = []
        for d in days:
            string = 'weekday-' + d
            if string in request.POST.keys():
                dow.append(d)
        h1 = int(st_time[0:2])
        m1 = int(st_time[3:5])
        h2 = int(end_time[0:2])
        m2 = int(end_time[3:5])
        time = int(time)
        cal_slots = int(numpy.floor(((h2 * 60 + m2) - (h1 * 60 + m1)) / time))
        for n in range(cal_slots):
            if m1 != 0:
                t1 = str(h1) + str(m1)
            else:
                t1 = str(h1) + str(m1) + '0'
            m1 = m1 + time
            if m1 >= 60:
                m1 = m1 - 60
                h1 += 1
                if m1<10:
                    m1 = '0' + str(m1)
            if m1 != 0:
                t2 = str(h1) + str(m1)
            else:
                t2 = str(h1) + str(m1) + '0'
            data = table.scan(FilterExpression={'doc_id':email}).values()
            items = data['Items']
            l = len(str(email))
            num = 0
            for it in items:
                c = int(it['slotid'][l:])
                if (c>num):
                    num = c
            num += 1
            num = email + str(num)
            if len(t1) == 3:
                t1 = '0' + t1
            if len(t2) == 3:
                t2 = '0' + t2
            table.insertValues(values=[{
                'slotid': num,
                'doc_id': email,
                'start_time': t1,
                'end_time': t2,
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
                'slotid':id
            })
    response = redirect('/appointments/')
    return response

def find_day(date):
    day, month, year = (int(i) for i in date.split(' '))     
    dayNumber = calendar.weekday(year, month, day) 
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return (days[dayNumber]) 

# @isDoctor(0)
def check_avail(request):
    table = Table('slot_available')
    if request.method == "POST":
        city = request.POST['city_name']
        locality = request.POST['locality']
        spec = request.POST['spec']
        date = request.POST['date_app']
        data = table.scan(FilterExpression={'spec':spec}).values()
        items = data['Items']
        return render(request, "appointments/pat_book.html", {'items':items})
    return render(request, "appointments/pat_slots.html")

def create_doc(request):
    table = Table('slots')
    table2 = Table('slot_available')
    table.delete()
    table2.delete()
    fake = Faker()
    for i in range(1,1001):
        doc = fake.email()
        lat = str(fake.latitude())
        lon = str(fake.longitude())
        fees = random.randint(100, 1000)
        special = ['Allergists', 'Anesthesiologists', 'Cardiologists', 'Dermatologists', 'Endocrinologists', 
        'Family Physicians', 'Gastroenterologists', 'Hematologists', 'Infectious Disease Specialists', 'Internists', 
        'Medical Geneticists', 'Nephrologists', 'Neurologists', 'Obstetricians', 'Gynecologists', 
        'Oncologists', 'Ophthalmologists', 'Osteopaths', 'Otolaryngologists', 'Pathologists',
        'Pediatricians', 'Physiatrists', 'Plastic Surgeons', 'Podiatrists', 'Preventive Medicine Specialists', 
        'Psychiatrists', 'Pulmonologists', 'Radiologists', 'Rheumatologists', 'General Surgeons', 'Urologists']
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
                'days': dow,
                'lon': lon,
                'lat': lat}])
        table2.insertValues(values=[{
                'id': i,
                'doc_id': doc,
                'spec': spec,
                'start_time': t1,
                'end_time': t2,
                'fees': fees,
                'days': dow,
                'lon': lon,
                'lat': lat}])
        return HttpResponse("You have generated data")

