from django.urls import path,include
from django.contrib.auth.views import LoginView
from .views import login_view,base_view,logout_view

urlpatterns = [
    path('',base_view,name='base'),
    path('login',login_view,name='login'),
    path('logout',logout_view,name='logout'),
]