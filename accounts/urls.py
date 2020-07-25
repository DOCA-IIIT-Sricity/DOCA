from django.urls import path,include
from . import views

urlpatterns = [
    path('login/',views.login),
    path('signup/',views.signup),
    path('verifyotp/',views.verifyotp),
    path('forgot/',views.forgot),
    path('logout/',views.logout),
    path('logoutd/',views.logoutD),
    path('dmail/',views.sendDemoMail),
    path('changepassword/',views.changePassword),
    path('uploadDp/',views.uploadDp),
    path('apply/',views.apply),
    path('pHome/',views.PatientHome),
]