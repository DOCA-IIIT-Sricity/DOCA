from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from .models import Transaction
from . import paytm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
Merchant_key = settings.PAYTM_SECRET_KEY

def initiate_payment(request):
    if request.method == "POST":
        amount = int(request.POST['amount'])
        user = request.user
        transaction = Transaction.objects.create(made_by=user, amount=amount)
        transaction.save()
        merchant_key = settings.PAYTM_SECRET_KEY

        param_dict = (
            ('MID', settings.PAYTM_MERCHANT_ID),
            ('ORDER_ID', str(transaction.order_id)),
            ('CUST_ID', str(transaction.made_by.email)),
            ('TXN_AMOUNT', str(transaction.amount)),
            ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
            ('WEBSITE', settings.PAYTM_WEBSITE),
            # ('EMAIL', request.user.email),
            # ('MOBILE_N0', '9911223388'),
            ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
            ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
            # ('PAYMENT_MODE_ONLY', 'NO'),
        )
        param_dict = dict(param_dict)
        param_dict['CHECKSUMHASH'] = paytm.generate_checksum(param_dict, merchant_key)
        print(param_dict)
        return render(request, 'payments/redirect.html', {'param_dict': param_dict})

    return render(request, 'payments/pay.html')

@csrf_exempt
def callback(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = paytm.verify_checksum(response_dict, Merchant_key, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'payments/callback.html', {'response': response_dict})
