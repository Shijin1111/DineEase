from django.db import models
from django.contrib.auth.models import User

class Inmate(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    room_no = models.IntegerField()
    
class MessExpense(models.Model):
    month = models.DateField()
    total_expense = models.DecimalField(max_digits=10,decimal_places=2)
    
class Mess_Out(models.Model):
    inmate = models.ForeignKey(Inmate,on_delete=models.CASCADE)
    month = models.DateField()
    mess_out_count = models.IntegerField()

class Mess_Bill(models.Model):
    inmate = models.ForeignKey(Inmate,on_delete=models.CASCADE)
    month = models.DateField()
    mess_count = models.IntegerField()
    bill_amount = models.DecimalField(max_digits=10,decimal_places=2)
    