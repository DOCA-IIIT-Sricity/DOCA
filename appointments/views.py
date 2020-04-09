from django.shortcuts import render, HttpResponse, redirect
from accounts.decorators import isDoctor
# from boto3.dynamodb.conditions import Attr
# import boto3
from mongodb.mongolib import Table
import numpy
from accounts.decorators import getEmail

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
    response = redirect('/appointments/')
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
