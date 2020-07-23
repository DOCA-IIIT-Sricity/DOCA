from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("doc_slots/", views.doc_home, name="doc_home"),
    path("add/", views.add_slots, name="add_slots"),
    path("del/", views.del_slots, name="del_slots"),
    path("patient_slots/", views.check_avail, name="check_avail"),

    # path("create_doc/", views.create_doc, name="create_doc"),
]
