from django.shortcuts import render
from django.http import HttpResponse

def index(request):

    return render(request, 'mainpage.html')

dict_list=[]
def index1(request):
    if request.method == "POST":
        tab = request.POST['tab']
        dose = request.POST['dosage']
        frequency = request.POST['frequency']
        note = request.POST['note']
        
        dict = {'tab': tab,
                'dose':dose,
                'frequency':frequency,
                'note':note
                }
        dict_list.append(dict)
        print(dict_list)
    return HttpResponse('')


def modalsubmit(request):
    if request.method == "POST":
        data = request.POST['']
        print(data)
    return render(request,'mainpage.html')