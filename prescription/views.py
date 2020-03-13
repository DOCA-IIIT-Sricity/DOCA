from django.shortcuts import render,render_to_response
from django.http import HttpResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource('dynamodb')
med_table = dynamodb.Table('Medicine')
symp_table = dynamodb.Table('symptoms')
pres_table = dynamodb.Table('prescription')

def listToString(s):
    str1 = ""

    for ele in s:
        str1 += ele

    return str1


def index(request):
    if request.method == "POST":
        notes = request.POST['dis_notes']
        symptoms = request.POST['pres_symp']
        medicine = request.POST['pres_med']
        symptoms = listToString(symptoms)
        count = pres_table.item_count
        print('after count')
        p_id = 'prescription_'+str(count)
        u_id = 'user_00'
        appoint_id = 'appoint_00'

        print('above put')
        pres_table.put_item(
            Item={
                'prescription_id' : p_id,
                'user_id' : u_id,
                'app_id' : appoint_id,
                'symptoms' : symptoms,
                'notes' : notes,
                'tabs' : medicine,
            }
        )
        print('put done')
        return render(request,'1.html')
    return render(request,'mainpage.html')


def dropdown(request):
    if request.method == "POST":
        send_list = []
        word = request.POST['word']
        response = med_table.scan(
        FilterExpression = Attr('name').contains(word)
        )
        items = response['Items']
        for dude in items:
            send_list.append(dude['name'])
        return render_to_response('dropdown.html',{'items' : send_list})


def dropdown_med(request):
    if request.method == "POST":
        send_list = []
        word = request.POST['word']
        response = med_table.scan(
        FilterExpression = Attr('name').contains(word)
        )
        items = response['Items']
        for dude in items:
            send_list.append(dude['name'])
        return render_to_response('dropdown_med.html',{'items' : send_list})
