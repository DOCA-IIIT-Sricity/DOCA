from django.urls import path,include
from . import views

urlpatterns = [
    path('tokenPair/',views.getTokenPair),
    path('primaryToken/',views.getPrimaryToken),
    path('register/',views.register),
    path('spec/',views.getSpecialization),
    path('city/',views.getCities),
    path('slots/', views.slots_list),
    path('appointments/', views.appoint_list),
    path('med/', views.med_list),
    path('symp/', views.symp_list),
    path('pres_table/', views.pres_table_list),
]