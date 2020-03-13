from django.urls import path
from  . import views

app_name = "prescription"

urlpatterns = [
    path('', views.index, name = 'index'),
    path('a',views.dropdown,name = 'dropdown'),
    path('b',views.dropdown_med,name = 'dropdown_med'),
]