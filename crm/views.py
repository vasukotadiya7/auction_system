from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
 
from . forms import CreateUserForm , LoginForm,AuthenticationForm

from django.contrib.auth.decorators import login_required

# Authenticate models and functions

from django.contrib.auth.models import auth,User
from .models import CustomUser
from django.contrib.auth import authenticate, login ,logout

# For contact_us Message and messagetags

from .models import Contact
from .models import CustomUser
from django.contrib import messages

# Email

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from elevate.settings import EMAIL_HOST_USER
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 

# Profile

from .forms import UserUpdateForm,ProfileUpdateForm
from .decorators import unauthenticated_user, allowed_users

#Product

from .models import Profile,Category,Seller,Product,Bid,ShippingDetails,Payment
from .forms import ProductForm,ShippingDetailsForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from datetime import datetime

from django.db.models import Q
from .forms import BidForm
import razorpay
from django.conf import settings 



@unauthenticated_user
def homepage(request):
 
    return render(request,'crm/index.html')

@unauthenticated_user
def about_us(request):
 
    return render(request,'crm/about_us.html')

@unauthenticated_user
def contact_us(request):

    if request.method=='POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        print(first_name, last_name, email , phone, message)


        if len(first_name)<2 or len(last_name)<2 or len(email)<5 or len(phone)<10 or len(message)<4:
            messages.error(request,"Please fill the form correctly ")
        else:
            
            contact = Contact(first_name=first_name,last_name=last_name,email=email,phone=phone,message=message)
            contact.save()
            messages.success(request,"Thank you for your response")
        
    return render(request,'crm/contact_us.html')


@unauthenticated_user
def registration(request):

    form = CreateUserForm()

    if request.method == 'POST':

        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # birthday = request.POST.get('birthday')
        # address = request.POST.get('address')


        form = CreateUserForm(request.POST)

        if form.is_valid():

            otp = random.randint(100000,999999)
            send_mail("User data: ",f"Verify your email by otp: \n{otp}",EMAIL_HOST_USER,[email],fail_silently=True)

            return render(request,'crm/verify.html',{'otp':otp,'first_name':first_name,'last_name':last_name,'username':username,'email':email,'password1':password1,'password2':password2})
        else :
            messages.error(request,"Please fill all the details correctly.  Choosing a hard-to-guess, but easy-to-remember password is important!")


    context = {'registerform' :form}

    return render(request,'crm/registration.html',context=context)

@csrf_exempt
def verify(request):

    if request.method == "POST":
        userotp = request.POST.get('otp')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # birthday = request.POST.get('birthday')
        # address = request.POST.get('address')

        if(password1 == password2):
            
            hashed_password = make_password(password1)
            form = User(first_name=first_name,last_name=last_name,username=username,email=email,password=hashed_password)
            form.save()

        print("OTP",userotp)
    return JsonResponse({'data': 'Hello'}, status=200)

@unauthenticated_user
def my_login(request):
    
    form = LoginForm()
    if request.method == 'POST':

        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:

                login(request, user)
                return redirect("dashboard")

    context = {'loginform' :form} 

    return render(request,'crm/my_login.html',context=context)

def user_logout(request):

    auth.logout(request)

    return redirect("")




@login_required(login_url="my_login")
def dashboard(request):

    return render(request,'crm/dashboard.html')


@login_required(login_url="my_login")
def profile(request):

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')


    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        

    context = {
        'u_form':u_form,
        'p_form':p_form
    }
    return render(request,'crm/profile.html',context)

@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def add_product(request):
 
    categories = Category.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.user,request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Don't commit to database yet
            product.user = request.user  # Set the user field to the current user
            date = form.cleaned_data['date']
            tomorrow = timezone.now().date() + timedelta(days=1)
            if date < tomorrow:
                form.add_error('date', _('Date must be a future date starting from tomorrow.'))
                return render(request, 'crm/add_product.html', {'form': form, 'categories': categories})
            product.save()  # Now save the product with the user assigned
            # Notify all users
            notify_users(product)

            messages.success(request, 'Product added successfully!')
            return redirect('add_product')

        else:
            # Form is invalid, render the form with errors
            error_message = "Please correct the errors below."
            return render(request, 'crm/add_product.html', {'form': form, 'error_message': error_message})  
    else:
        form = ProductForm(request.user)  
    
    return render(request, 'crm/add_product.html', {'form': form,'categories' :categories,
})

def notify_users(product):
    users = User.objects.exclude(id=product.user.id)  # Exclude the product owner
    recipient_list = [user.email for user in users if user.email]

    subject = "New Product Alert!"
    message = f"A new product '{product.name}' has been listed by {product.user.username}. Check it out on the auction platform!"
    print(recipient_list)
    if recipient_list:
        send_mail(subject, message, EMAIL_HOST_USER, ["vasukotadiya224@gmail.com","yt224prem@gmail.com"])

@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def my_products(request):

    # products = Product.objects.all()
    # Get the current time
    current_datetime = datetime.now()

    # Filter products based on their time status
    live_products = Product.objects.filter(user=request.user,date=current_datetime.date(), start_time__lte=current_datetime.time(), end_time__gte=current_datetime.time())
    upcoming_products = Product.objects.filter(user=request.user,date__gt=current_datetime.date())
    closed_products = Product.objects.filter(
        Q(user=request.user) &  # Filter by current user
        (
            Q(date__lt=current_datetime.date()) |  # Date is in the past
            (Q(date=current_datetime.date()) & Q(end_time__lt=current_datetime.time()))  # Date is today, end time has passed
        )
    )
    print("Closed Products Count:", closed_products.count())  # Debug output
    default_option = "live"  # Example default option


    context = {
        'live_products': live_products,
        'upcoming_products': upcoming_products,
        'closed_products': closed_products,
        'default_option': default_option,
    }


    return render(request, 'crm/my_products.html',context)

@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def my_bids(request):
    # Get the current user
    user = request.user

    # Get live products on which the user has bid
    live_bids = Bid.objects.filter(user=user, product__date=datetime.now().date(), product__start_time__lte=datetime.now().time(), product__end_time__gte=datetime.now().time())

    # Get closed products on which the user has bid
    closed_bids = Bid.objects.filter(user=user).exclude(product__date=datetime.now().date(), product__start_time__lte=datetime.now().time(), product__end_time__gte=datetime.now().time())
    
    default_option = "live"  # Example default option

    context = {
        'live_bids': live_bids,
        'closed_bids': closed_bids,
        'default_option': default_option,

    }

    return render(request, 'crm/my_bids.html', context)



@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def auction(request):

    categories = Category.objects.all()


    current_datetime = datetime.now()
    # Filter products based on their time status
    live_products = Product.objects.filter(date=current_datetime.date(), start_time__lte=current_datetime.time(), end_time__gte=current_datetime.time())[:4]
    upcoming_products = Product.objects.filter(date__gt=current_datetime.date())[:4]
    closed_products = Product.objects.filter(
        (
            Q(date__lt=current_datetime.date()) |
            (Q(date=current_datetime.date()) & Q(end_time__lt=current_datetime.time()))
        )
    )[:4]


    context = {
        'live_products': live_products,
        'upcoming_products': upcoming_products,
        'closed_products': closed_products,
        "categories" :categories,
    }

    return render(request, 'crm/auction.html',context)

@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def category_view(request,cid):

    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(Category=category)


    default_option = "live"  # Example default option

    current_datetime = datetime.now()
    # Filter products based on their time status
    live_products = products.filter(date=current_datetime.date(), start_time__lte=current_datetime.time(), end_time__gte=current_datetime.time())
    upcoming_products = products.filter(date__gt=current_datetime.date())
    closed_products = products.filter(
        (
            Q(date__lt=current_datetime.date()) |
            (Q(date=current_datetime.date()) & Q(end_time__lt=current_datetime.time()))
        )
    )

    context = {
        'category':category,
        'products':products,
        'live_products': live_products,
        'upcoming_products': upcoming_products,
        'closed_products': closed_products,
        'default_option': default_option,    
    }


    return render(request, 'crm/category_view.html',context)

@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def product_detail(request,pid):
    
    product = Product.objects.get(pid=pid)
    current_datetime = datetime.now()
    
    # Debug print statements
    # print("Current Date:", current_datetime.date())
    print("Current Time:", current_datetime.time())
    # print("Product Date:", product.date)
    # print("Product Start Time:", product.start_time)
    # print("Product End Time:", product.end_time)

    # Check if the product is live, upcoming, or closed
    if product.date == current_datetime.date():
        if current_datetime.time() < product.start_time:
            product_status = "Upcoming"
        elif current_datetime.time() > product.end_time:
            product_status = "Closed"
        else:
            product_status = "Live"
    elif product.date < current_datetime.date():
        product_status = "Closed"
    else:
        product_status = "Upcoming"

    print("Product Status:", product_status)  # Debug print statement

    # if product_status == "Closed":
    #     return redirect('closed_product_detail', pid=pid)
    # elif product_status == "Upcoming":
    #     return redirect('coming_soon_product_detail', pid=pid)
    # elif product_status == "Live":
        # Render the product detail page for live products
    context = {
            'product': product,
            'product_status': product_status,
            'form': BidForm(),  # Add this line to pass the BidForm instance

        }
    return render(request, 'crm/product_detail.html', context)


# def closed_product_detail(request,pid):
#     return render(request, 'crm/closed_product_detail.html')

# def coming_soon_product_detail(request,pid):
#     return render(request, 'crm/coming_soon_product_detail.html')
    
@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])    
def place_bid(request, pid):
    if request.method == 'POST':
        # Step 1: Retrieve the product object based on the pid from the request
        try:
            product = Product.objects.get(pid=pid)
        except Product.DoesNotExist:
            # Handle the case where the product with the given pid does not exist
            messages.error(request, 'The product does not exist.')
            return redirect('product_detail', pid=pid)
        print("2")
        # Step 2: Check if the product is live for bidding
        if product.is_live_for_bidding():
            # Step 3: Initialize the bid form with the POST data
            print("3")
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                # Step 4: Extract the bid amount from the form data
                amount = bid_form.cleaned_data['amount']
                print("4")
                # Step 5: Check if the bid amount is valid
                if product.is_valid_bid(amount):
                    # Step 6: Save the bid to the database
                    print("5")
                    if(request.user == product.user):
                        messages.error(request, 'You cannot bid on your own product.')
                        return redirect('product_detail', pid=pid)
                    
                    Product.place_bid(user=request.user, product=product, amount=amount)

                    # Step 8: Display a success message and redirect to the product detail page
                    messages.success(request, 'Your bid has been successfully placed.')
                    return redirect('product_detail', pid=pid)
                else:
                    # Handle the case where the bid amount is not valid
                    messages.error(request, f'Your bid amount must be at least {product.price_interval} higher than the current highest bid.')
            else:
                # Handle the case where the bid form is invalid
                messages.error(request, 'Invalid bid amount. Please enter a valid amount.')
        else:
            # Handle the case where bidding for the product is closed
            messages.error(request, 'Bidding for this product is closed.')
    
    # Redirect to the product detail page if the request method is not POST
    return redirect('product_detail', pid=pid)


@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def shipping_details(request,pid):

    product = Product.objects.get(pid=pid)


    if request.method == 'POST':
        form = ShippingDetailsForm(request.POST)
        if form.is_valid():
            shipping_details = form.save(commit=False)
            shipping_details.user = request.user
            shipping_details.product = product  # Associate with the product
            shipping_details.save()
            messages.success(request, 'Shipping details submitted successfully.')
            return redirect('payment',pid=pid)

            # Create Razorpay order
            

            # if shipping_details is not None:  # Check if shipping_details is assigned a value
            #     shipping_details.razor_pay_order_id = payment['id']
            #     shipping_details.save()

    else:
        form = ShippingDetailsForm()

    # client = razorpay.Client(auth=(settings.KEY, settings.SECRET_KEY))
    # # amount_in_paise =   # Convert amount to integer paise
    # payment = client.order.create({'amount': winner_product.highest_bid * 100, 'currency': 'INR', 'payment_capture': 1})
    # print(payment)

    context = {
        'form': form,
        'winner': product.winner_details,  # Assuming product has a winner_details field
        'winner_product': product
    }

    return render(request, 'crm/shipping_details.html', context)

@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def success(request):
    
    return render(request, 'crm/success.html')


@login_required(login_url="my_login")
@allowed_users(allowed_roles=['Admin','Customer'])
def payment(request, pid):
    product = Product.objects.get(pid=pid)
    amount = product.highest_bid * 100  # Calculate the amount

    client = razorpay.Client(auth=(settings.KEY, settings.SECRET_KEY))
    payment_response = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})

    # Save payment information
    payment = Payment.objects.create(
        user=request.user,  # Set the user to the current user
        product=product, 
        razor_pay_order_id=payment_response['id'],
        paid=False  # Set as False initially
    )

    context = {
        'product': product,
        'amount': amount,
        'payment': payment,
    }

    if request.method == 'POST':
        # Process the payment
        # Assuming the payment is successful, update the paid field
        payment.paid = True
        payment.save()

        # Redirect to a success page or do any other necessary action
        return redirect('success')  # Change 'payment_success' to the appropriate URL name for success page

    return render(request, 'crm/payment.html', context)
