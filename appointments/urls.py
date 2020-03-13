from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.doc_home, name="doc_home"),
    path("add/", views.add_slots, name="add_slots"),
    path("del/", views.del_slots, name="del_slots"),
]
