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
        c += 1
    return render(request, "appointments/doc_slots.html", {'items':items})

