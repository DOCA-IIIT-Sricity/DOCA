from django.urls import path,include
from . import views

urlpatterns = [
    path('login/',views.login),
    path('signup/',views.signup),
    path('verifyotp/',views.verifyotp),
    path('forgot/',views.forgot),
    path('logout/',views.logout),
    path('dmail/',views.sendDemoMail),
    path('changepassword/',views.changePassword),
    
]