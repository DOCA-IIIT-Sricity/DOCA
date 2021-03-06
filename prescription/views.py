from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from pymongo import MongoClient
from mongodb.mongolib import Table


def listToString(s):
    str1 = ""

    for ele in s:
        str1 += ele

    return str1

app_id = ""

def index(request):
    appointment_id = print(request.GET.get('app_id'))
    if request.method == "POST":
        table = Table('pres_table')
        notes = request.POST['dis_notes']
        symptoms = request.POST['pres_symp']
        medicine = request.POST['pres_med']
        name = request.POST['name']
        age = request.POST['age']
        sex = request.POST['sex']
        print(name,age,sex)
        symptoms = listToString(symptoms)
        table.insertValues(values=[
            {
                'name' : name,
                'age' : age,
                'sex':sex,
                'app_id' : appoint_id,
                'symptoms' : symptoms,
                'notes' : notes,
                'tabs' : medicine,
            }]
        )
        print('put done')
        return render(request,'appointments/dashboard.html')
    return render(request,'prescription/mainpage.html')


def dropdown(request):
    if request.method == "POST":
        send_list = []
        word = request.POST['word']
        table = Table('symp')
        res = table.scan({})
        print(res)
        for dude in res.values()['Items']:
            if word in dude['symp']:
                send_list.append(dude['symp'])
        print(send_list)
        return render(None,'prescription/dropdown.html',{'items' : send_list})


def dropdown_med(request):
    if request.method == "POST":
        send_list = []
        word = request.POST['word']
        table = Table('med')
        res = table.scan({})
        for dude in res.values()['Items']:
            if word in dude['med']:
                send_list.append(dude['med'])
        return render(None,'prescription/dropdown_med.html',{'items' : send_list})
