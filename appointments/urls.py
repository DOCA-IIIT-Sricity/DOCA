from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("doc_slots/", views.doc_home, name="doc_home"),
    path("add/", views.add_slots, name="add_slots"),
    path("del/", views.del_slots, name="del_slots"),
    path("pat_slots/", views.check_avail, name="check_avail"),
    path("appoint/", views.appoint, name="appoint"),
    path("check_app/", views.check_appointments, name="check_app"),
    path("del_app/", views.cancel_appointments, name="cancel_app"),

    # path("create_doc/", views.create_doc, name="create_doc"),
]
