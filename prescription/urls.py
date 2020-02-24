from django.urls import path
from  . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('moda/',views.modalsubmit, name = "add"),
    path('am/',views.index1, name = 'index1'),
]