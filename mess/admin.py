from django.contrib import admin
from mess.models import Inmate,Mess_Bill,MessExpense,Mess_Out

admin.site.register(Inmate)
admin.site.register(Mess_Bill)
admin.site.register(MessExpense)
admin.site.register(Mess_Out)