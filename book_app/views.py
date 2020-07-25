from django.shortcuts import render
from accounts.decorators import isDoctor,getEmail
from mongodb.mongolib import Table
from datetime import datetime

@isDoctor(0)
def Appointemets(request):
    uid=getEmail(request.session['session_key'])
    table = Table('appointments')
    appointments = table.scan(FilterExpression={'user_id':uid}).values()
    rdict={}
    if appointments['Count']!=0:
        rdict={'appointements':appointments['Items']}
    return render(request,'book_appointement/pat_Appointement.html',rdict)

@isDoctor(0)
def SearchDoctor(request):
    
    if "spec" in request.GET and "city" in request.GET and 'date' in request.GET:
        specialization = request.GET['spec']
        city = request.GET['city']
        date0 = request.GET['date']
        
        date = datetime.strptime(date0, '%Y-%m-%d')
        
        table = Table('doctor')
        
        results = table.scan(FilterExpression={"spec":specialization,'city':city}).values()
        
        data=[]
        
        for result in results['Items']:
            weekdays = ['mon','tue','wed','thu','fri','sat','sun']
            slotTable = Table('slots')
            
            appointement_helper = Table('appointement_helper')
            slots_Available = 0
            result2 = appointement_helper.scan(FilterExpression={
                'doc_id':result['doc_id'],
                'date': date0,
            }).values()
            
            if result2['Count'] == 0:
                results0 = slotTable.scan(FilterExpression={
                    'doc_id': result['doc_id'],
                    }).values()
                scount = 0
                availableSlots=[]
                for day in results0['Items']:
                    print(weekdays[date.weekday()-1])
                    print(day)
                    if weekdays[date.weekday()] in day['days']:
                        availableSlots.append({
                            "slot_id": day['slot_id'],
                            "start_time":day['start_time'],
                            "end_time":day["end_time"],
                            "fee":day['fees']
                        })
                        scount+=1;
                slots_Available = scount
                
                appointement_helper.insertValues(values=[{
                    'id':result['doc_id']+date0,
                    'date':date0,
                    'doc_id':result['doc_id'],
                    'avilableSlots':availableSlots,
                }])
            else:
               slots_Available  = len(result2['Items'][0]['avilableSlots'])
               
               
                
                
            data.append({
                'doc_id':  result['doc_id'],
                'name': "Dr."+result['first_name']+" "+result['last_name'],
                'address': result['address']+","+result['city'],
                'spec': result['spec'],
                "slotAvailabe":slots_Available,
                'experience':'9+ year Experience',
                'rating':96,
                'fee':300,         
            })
            
        print(data)
               
        return render(request,'book_appointement/doctor_list.html',{'doctors':data,'date':date0})
    
    else:
        return render(request,'book_appointement/b_app_find.html')
    
    
@isDoctor(0)    
def slots_Available(request):
    if 'doc_id' in request.GET and 'date' in request.GET:
        docTable = Table('doctor')
        result = docTable.scan(FilterExpression={'doc_id':request.GET['doc_id']}).values()['Items'][0]
        
        doc = {
                'doc_id':  result['doc_id'],
                'name': "Dr."+result['first_name']+" "+result['last_name'],
                'address': result['address']+","+result['city'],
                'spec': result['spec'],
                "slotAvailabe":slots_Available,
                'experience':'9+ year Experience',
                'rating':96,
                'fee':300,         
            }
        
        appointement_helper = Table('appointement_helper')
        
        result2 = appointement_helper.scan(FilterExpression={
            'doc_id':result['doc_id'],
            'date': request.GET['date'],
        }).values()['Items'][0]['avilableSlots']
        
        return render(request,'book_appointement/select_slot.html',{'slots':result2,'doc':doc,'date':request.GET['date'],})
    
@isDoctor(0)
def confirm(request):
    if 'doc_id' in request.GET and 'date' in request.GET and 'slot_id' in request.GET:
        
        user_id = getEmail(request.session['session_key'])
        
        docTable = Table('doctor')
        result = docTable.scan(FilterExpression={'doc_id':request.GET['doc_id']}).values()['Items'][0]
        date  = request.GET['date']
        
        appointement_helper = Table('appointement_helper')
        
        result3 = appointement_helper.scan(FilterExpression={
            'doc_id':result['doc_id'],
            'date': request.GET['date'],
        }).values()['Items'][0]['avilableSlots']
        
        slot = []
        
        for res in result3:
            if res['slot_id'] == request.GET['slot_id']:
                result3.remove(res)
                slot = res
        
        appointement_helper.delete(FilterExpression={'doc_id':result['doc_id'],
            'date': request.GET['date'],})
        
        appointement_helper.insertValues(values=[{
                    'id':result['doc_id']+date,
                    'date':date,
                    'doc_id':result['doc_id'],
                    'avilableSlots':result3,
                }])
        
        appointementTable = Table('appointments')
        
        appointementTable.insertValues(values=[{
            'id':"u"+user_id+'d'+result['doc_id']+'on'+date+'slot'+slot['slot_id'],
            'user_id':user_id,
            'doctor':result,
            'slot': slot,
            'date':date,
        }])
        
        return render(request,'book_appointement/confirm.html',{'doc': result,'slot':slot,'date':date})
        
    else:
        return render(request,'global/400.html')
        
        
        
        
        
        
        
        
        
        
        
        