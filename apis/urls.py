from django.urls import path,include
from . import views

urlpatterns = [
    path('tokenPair/',views.getTokenPair),
    path('primaryToken/',views.getPrimaryToken),
    path('register/',views.register),
    path('slots/', views.slots_list),
]