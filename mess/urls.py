from django.urls import path,include
from django.contrib.auth.views import LoginView
from .views import login_view,base_view,logout_view,home_view,mess_bill_view,mess_out_view,payment_success,create_payment

urlpatterns = [
    path('',base_view,name='base'),
    path('login',login_view,name='login'),
    path('logout',logout_view,name='logout'),
    path('mess_out',mess_out_view,name='mess_out'),
    path('mess_bill',mess_bill_view,name='mess_bill'),    
    path('payment', payment_success, name='payment'),
    path('create_payment/<int:bill_id>/',create_payment,name='create_payment')
]