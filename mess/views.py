from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import Mess_out_form
from .models import Mess_Out,Mess_Bill
from django.contrib.auth.decorators import login_required
import razorpay
# Create your views here.
def base_view(request):
    return render(request,'base.html')
def home_view(request):
    return render(request,'home.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            return render(request,'base.html')
        else:
            messages.error(request,"invalid username or password")
            return redirect('login')
    return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def mess_bill_view(request):
    inmate = request.user.inmate
    mess_bills = Mess_Bill.objects.filter(inmate=inmate)
    return render(request,'mess_bill.html',{'mess_bills':mess_bills})

@login_required
def mess_out_view(request):
    if request.method == 'POST':
        form = Mess_out_form(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            messout_count = (end_date-start_date).days
            inmate = request.user.inmate
            #  Attribute names in Django are case-sensitive,and 
            #  Django automatically assigns the reverse relation name in lowercase by default.
            #  therefore Inmate model is given as inmate for attribute
            Mess_Out.objects.create(
                inmate = inmate,
                month = start_date,
                mess_out_count = messout_count,
            )
    else:
        form = Mess_out_form()
    return render(request,'mess_out.html',{'form':form})


from datetime import date
import calendar
from django.db.models import Sum
from .models import Mess_Out, Inmate, MessExpense, Mess_Bill

def calculate_mess_bills():
    # Define the month and year for which you want to calculate
    year = 2024
    month = 12
    Mess_Bill.objects.filter(month__year=year, month__month=month).delete()

    # Get the total days in the month
    _, total_days_in_month = calendar.monthrange(year, month)

    # Get the total expense for the month
    mess_expense = MessExpense.objects.filter(month__year=year, month__month=month).first()
    # The __year and __month syntax is used in Django to refer to specific components of a DateTimeField or DateField.
    if not mess_expense:
        raise ValueError("No expense data found for the given month")

    # Get all Mess_Out records for the month
    mess_out_records = Mess_Out.objects.filter(month__year=year, month__month=month)

    # Calculate total presence days across all inmates
    total_presence_days = 0
    inmate_presence_data = []
    inmates = Inmate.objects.all()
    # Assuming `all_inmates` is a list of all inmates in the month (including those without mess-out records)
    for inmate in inmates:
        # Find if the inmate has any mess-out records
        mess_out = [m for m in mess_out_records if m.inmate == inmate]
        
        if mess_out:
            # Inmate has mess-out records
            total_mess_out_count = sum(mess_out.mess_out_count for mess_out in mess_out)
            presence_days = total_days_in_month - total_mess_out_count
        else:
            # Inmate has no mess-out records, assume full presence for the month
            presence_days = total_days_in_month
        
        # Accumulate the total presence days
        total_presence_days += presence_days
        
        # Store the data for the inmate
        inmate_presence_data.append({
            'inmate': inmate,
            'presence_days': presence_days,
        })

    if total_presence_days == 0:
        raise ValueError("No presence days found for the month")

    # Calculate cost per day
    cost_per_day = mess_expense.total_expense / total_presence_days
    print(total_presence_days)
    # Calculate and save bills for each inmate
    for data in inmate_presence_data:
        bill_amount = cost_per_day * data['presence_days']
        Mess_Bill.objects.create(
            inmate=data['inmate'],
            month=date(year, month, 1),
            mess_count = data['presence_days'],
            bill_amount=bill_amount
        )
    print(f"Mess bills calculated and saved for {month}/{year}")


import razorpay
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Initialize Razorpay client with your credentials
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment(request, bill_id):
    # Retrieve the bill details based on the provided bill_id
    try:
        bill = Mess_Bill.objects.get(id=bill_id)
    except Mess_Bill.DoesNotExist:
        return JsonResponse({"error": "Bill not found"}, status=404)

    if request.method == "GET":
        # Convert the amount to paise (multiplying by 100) and ensure it's a float
        amount = float(bill.bill_amount) * 100  # Convert to paise (in float)

        currency = "INR"
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": int(amount),  # Razorpay expects the amount to be an integer
            "currency": currency,
            "payment_capture": "1"  # Auto-capture payment
        })

        context = {
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": bill.bill_amount,  # Send amount in rupees to template
        }
        return render(request, "payment_page.html", context)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        # Handle the success webhook or response
        data = request.POST
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")
        
        # Verify the payment signature
        try:
            razorpay_client.utility.verify_payment_signature(data)
            # Payment is successful, save details in the database
            return JsonResponse({"status": "success", "payment_id": razorpay_payment_id})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "failed", "error": "Invalid signature"})
    return JsonResponse({"error": "Invalid request"}, status=400)
