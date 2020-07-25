from django.urls import path
from . import views

app_name = "book_app"

urlpatterns = [
   path("search/",views.SearchDoctor),
   path('select/',views.slots_Available),
   path('confirm/',views.confirm)
   
]
