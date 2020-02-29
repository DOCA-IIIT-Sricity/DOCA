from django.shortcuts import render
from accounts.decorators import isDoctor
from boto3.dynamodb.conditions import Attr
import boto3

# Create your views here.
@isDoctor(1)
def doc_home(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Slots')
    email = request.session['email']
    print(table.creation_date_time)
    response = table.scan(
        FilterExpression = Attr('doc_id').eq(email)
    )
    items = response['Items']
    c = 1
    for item in items:
        item['num'] = c
        item['start_time'] = item['start_time'][0:2] + ":" + item['start_time'][2:4]
        item['end_time'] = item['end_time'][0:2] + ":" + item["end_time"][2:4]
        item['fees'] = item['fees'] + u"\u20B9"
        c += 1
    return render(request, "appointments/doc_slots.html", {'items':items})

