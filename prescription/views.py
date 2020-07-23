from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from pymongo import MongoClient
client = pymongo.MongoClient("localhost",27017)
db = client.SOAD


#
# dynamodb = boto3.resource('dynamodb')
# med_table = dynamodb.Table('Medicine')
# symp_table = dynamodb.Table('symptoms')
# pres_table = dynamodb.Table('prescription')

def listToString(s):
    str1 = ""

    for ele in s:
        str1 += ele

    return str1


def index(request):
    if request.method == "POST":
        collection = db.pres_table
        notes = request.POST['dis_notes']
        symptoms = request.POST['pres_symp']
        medicine = request.POST['pres_med']
        symptoms = listToString(symptoms)
        # count = pres_table.item_count
        # print('after count')
        # p_id = 'prescription_'+str(count)
        p_id = 1
        u_id = 'user_00'
        appoint_id = 'appoint_00'
        #
        # print('above put')
        # pres_table.put_item(
        #     Item={
        #         'prescription_id' : p_id,
        #         'user_id' : u_id,
        #         'app_id' : appoint_id,
        #         'symptoms' : symptoms,
        #         'notes' : notes,
        #         'tabs' : medicine,
        #     }
        # )
        collection.insert_one(
            {
                'prescription_id' : p_id,
                'user_id' : u_id,
                'app_id' : appoint_id,
                'symptoms' : symptoms,
                'notes' : notes,
                'tabs' : medicine,
            }
        )
        print('put done')
        return render(request,'prescription/1.html')
    return render(request,'prescription/mainpage.html')


def dropdown(request):
    if request.method == "POST":
        send_list = []
        word = request.POST['word']
        collection = db.symp
        res = collection.find({})
        # response = med_table.scan(
        # FilterExpression = Attr('name').contains(word)
        # )
        # items = response['Items']
        for dude in res:
            send_list.append(dude['symp'])
        return render(None,'prescription/dropdown.html',{'items' : send_list})


def dropdown_med(request):
    if request.method == "POST":
        send_list = []
        word = request.POST['word']
        collection = db.med
        res = collection.find({})
        # response = med_table.scan(
        # FilterExpression = Attr('name').contains(word)
        # )
        # items = response['Items']
        for dude in res:
            send_list.append(dude['tab'])
        return render(None,'prescription/dropdown_med.html',{'items' : send_list})
