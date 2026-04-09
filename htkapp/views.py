# Django core
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
# Authentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Database & ORM
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
# Forms
from .forms import CheckoutForm, ContactForm, ProductForm
# Models
from .models import (
    Product, CartItem, UserProfile, Category,
    Order, OrderItem, Coupon, Testimonial
)
# Email
from django.core.mail import send_mail
# Utilities
import json
import random
import re
import io
import os
from datetime import timedelta
# PDF
try:
    from xhtml2pdf import pisa
except:
    pisa = None
from reportlab.pdfgen import canvas
# Admin decorator
from .decorators import admin_required
# Create your views here.


def home(request):
    # ✅ redirect admin
    if request.user.is_superuser:
        return redirect("admin_dashboard")

    # ✅ Featured products ONLY (no fallback to show selection matters)
    products = Product.objects.filter(is_featured=True)[:6]
    
    categories = Category.objects.all()
    testimonials = Testimonial.objects.all()  

    return render(request, "home.html", {
        "products": products,
        "testimonials": testimonials,
        "categories": categories
    })
def register(request):

    if request.method == "POST":

        email = request.POST.get('email')
        entered_otp = request.POST.get('email_otp')
        phone = request.POST.get('phone')
        country_code = request.POST.get('country_code')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        session_otp = request.session.get("email_otp")

        context = {
            "email": email,
            "phone": phone,
            "country_code": country_code
        }

        # empty fields
        if not email or not entered_otp or not phone or not password or not confirm_password:
            messages.error(request,"All fields are required")
            return render(request,"register.html",context)

        # ✅ email format validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request,"Enter a valid email address")
            return render(request,"register.html",context)

        # otp check
        if str(entered_otp) != str(session_otp):
            messages.error(request,"Invalid OTP")
            return render(request,"register.html",context)

        # phone validation
        if not re.match(r'^\d{10}$', phone):
            messages.error(request,"Phone number must be 10 digits")
            return render(request,"register.html",context)

        # duplicate phone check
        if UserProfile.objects.filter(phone=phone).exists():
            messages.error(request,"Phone number already registered")
            return render(request,"register.html",context)

        # password length
        if len(password) < 8:
            messages.error(request,"Password must be at least 8 characters")
            return render(request,"register.html",context)

        # strong password validation
        if not re.search(r'[A-Z]', password):
            messages.error(request,"Password must contain at least one uppercase letter")
            return render(request,"register.html",context)

        if not re.search(r'[0-9]', password):
            messages.error(request,"Password must contain at least one number")
            return render(request,"register.html",context)

        # password match
        if password != confirm_password:
            messages.error(request,"Passwords do not match")
            return render(request,"register.html",context)

        # existing user
        if User.objects.filter(username=email).exists():
            messages.error(request,"Email already registered")
            return render(request,"register.html",context)

        # create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # create profile
        UserProfile.objects.create(
            user=user,
            country_code=country_code,
            phone=phone,
            email_verified=True
        )

        messages.success(request,"Account created successfully")

        return redirect("home")

    return render(request,"register.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # ✅ ADMIN REDIRECT
            if user.is_superuser:
                return redirect("admin_dashboard")

            # ✅ NORMAL USER
            messages.success(request, "Login Successful")
            return redirect("home")

        else:
            messages.error(request, "Invalid email or password")

    return redirect("home")

def user_logout(request):
    logout(request)
    return redirect('home')


def send_email_otp(request):

    if request.method == "POST":

        data = json.loads(request.body)
        email = data.get("email")

        # ✅ check empty
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # ✅ validate email BEFORE sending
    

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|in|org|net)$', email):
            return JsonResponse({"error": "Enter a valid email address"}, status=400)

        # ✅ generate otp
        otp = random.randint(100000,999999)
        request.session["email_otp"] = otp
        # print(otp)

        #  send mail (safe now)
        try:
            send_mail(
                "HTK Farms OTP Verification",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
        except Exception as e:
            return JsonResponse({"error": "Failed to send OTP"}, status=500)

        return JsonResponse({"message": "OTP sent successfully"})
    
def verify_email_otp(request):
    if request.method=="POST":
        data=json.loads(request.body)
        entered_otp=data.get("otp")
        session_otp=request.session.get("email_otp")
        if str(entered_otp)==str(session_otp):
            request.session["otp_verified"] = True
            return JsonResponse({"status":"success"})
        else:
            return JsonResponse({"status":"failed"})
        
def products(request):
    category_id = request.GET.get("category")
    
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    categories = Category.objects.all()
    return render(request,"products.html",{
        "products":products,
        "categories":categories
    })
    

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "product_detail.html", {"product": product})


# @login_required
def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    cart_count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))

    return JsonResponse({
        "status": "success",
        "cart_count": cart_count
    })


@login_required
def cart(request):

    cart_items = CartItem.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        total += item.total_price 
    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })
    
def get_cart_count(request):

    if request.user.is_authenticated:
        count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        count = 0

    return {
        "cart_count": count
    }


def increase_quantity(request, id):

    item = CartItem.objects.get(id=id, user=request.user)
    item.quantity += 1
    item.save()

    return redirect("cart")

def decrease_quantity(request, id):

    item = CartItem.objects.get(id=id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")

def update_quantity(request, id, qty):

    item = CartItem.objects.get(id=id, user=request.user)

    item.quantity = qty
    item.save()

    return redirect("cart")

def remove_item(request, id):

    item = CartItem.objects.get(id=id, user=request.user)
    item.delete()

    return redirect("cart")


@login_required
def clear_cart(request):

    CartItem.objects.filter(user=request.user).delete()

    return redirect("cart")



def send_forgot_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        # ✅ check email exists
        if not User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email not registered"}, status=400)

        # ✅ generate otp
        otp = random.randint(100000, 999999)

        # ✅ store in session
        request.session["forgot_otp"] = otp
        request.session["reset_email"] = email

        # print("Forgot OTP:", otp)

        try:
            send_mail(
                "HTK Farms Password Reset OTP",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
        except:
            return JsonResponse({"error": "Failed to send OTP"}, status=500)

        return JsonResponse({"message": "OTP sent successfully"})

def verify_forgot_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        entered_otp = data.get("otp")

        session_otp = request.session.get("forgot_otp")

        if str(entered_otp) == str(session_otp):
            request.session["forgot_verified"] = True
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "failed"})
        
from django.contrib import messages
from django.shortcuts import render, redirect

from django.http import JsonResponse
import json

def reset_password(request):
    if request.method == "POST":

        if not request.session.get("forgot_verified"):
            return JsonResponse({"error": "Unauthorized"}, status=403)

        data = json.loads(request.body)

        password = data.get("password")
        confirm = data.get("confirm")

        if password != confirm:
            return JsonResponse({"error": "Passwords do not match"})

        email = request.session.get("reset_email")

        from django.contrib.auth.models import User
        user = User.objects.get(email=email)

        user.set_password(password)
        user.save()

        # clear session
        request.session.pop("forgot_otp", None)
        request.session.pop("forgot_verified", None)
        request.session.pop("reset_email", None)

        return JsonResponse({"message": "Password reset successful"})




@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    # ✅ subtotal
    subtotal = sum(item.total_price for item in cart_items)

    # coupon
    coupon_code = request.session.get("coupon_code")
    discount = 0

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            discount = (subtotal * coupon.discount_percent) / 100

            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)

            if discount >= subtotal:
                discount = subtotal - 1

        except Coupon.DoesNotExist:
            discount = 0

    # shipping
    shipping = 50 if subtotal < 499 else 0
    total = subtotal - discount + shipping

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():

            full_address = form.get_full_address()
            request.session["saved_name"] = form.cleaned_data["name"]
            request.session["saved_phone"] = form.cleaned_data["phone"]
            request.session["saved_pincode"] = form.cleaned_data["pincode"]
            request.session["saved_city"] = form.cleaned_data["city"]
            request.session["saved_state"] = form.cleaned_data["state"]
            request.session["saved_address1"] = form.cleaned_data["address_line1"]
            request.session["saved_address2"] = form.cleaned_data["address_line2"]
            request.session["saved_landmark"] = form.cleaned_data["landmark"]


            # ✅ CREATE ORDER
            order = Order.objects.create(
                user=request.user,
                name=form.cleaned_data["name"],
                total_price=total,
                address=full_address,
                phone=form.cleaned_data["phone"]
            )

            # 🔥 CRITICAL FIX: FORCE FRESH QUERY
            cart_items = CartItem.objects.filter(user=request.user)


            # 🔥 CREATE ORDER ITEMS
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            request.session["order_id"] = order.id
            

            return redirect("payment")
    else:
    # ✅ Get profile
        profile = UserProfile.objects.get(user=request.user)

        initial_data = {
            "name": profile.full_name or request.session.get("saved_name", ""),
            "phone": profile.phone or request.session.get("saved_phone", ""),
            "pincode": profile.pincode or request.session.get("saved_pincode", ""),
            "city": profile.city or request.session.get("saved_city", ""),
            "state": profile.state or request.session.get("saved_state", ""),
            "address_line1": profile.address_line1 or request.session.get("saved_address1", ""),
            "address_line2": profile.address_line2 or request.session.get("saved_address2", ""),
            "landmark": request.session.get("saved_landmark", ""),
        }

        form = CheckoutForm(initial=initial_data)

    return render(request, "checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount": int(discount),
        "shipping": shipping,
        "total": int(total),
    })

@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)

    return render(request, "order_success.html", {
        "order": order
    })
    
from django.shortcuts import get_object_or_404

@login_required
def payment(request):
    order_id = request.session.get("order_id")

    # ✅ Fix: check if order_id exists
    if not order_id:
        return redirect("cart")   # or checkout page

    # ✅ Safe fetch (no crash)
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.payment_method = request.POST.get("payment")
        order.is_paid = True
        order.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        request.session.pop("order_id", None)
        request.session.pop("coupon_code", None)

        return redirect("order_success", order_id=order.id)

    return render(request, "payment.html", {
        "total": int(order.total_price),
        "address": order.address,
        "phone": order.phone,
        "name": order.name
    })   
     
@login_required
def order_history(request):
    status = request.GET.get("status")

    orders = Order.objects.filter(user=request.user)

    if status and status != "all":
        orders = orders.filter(status=status)

    orders = orders.order_by('-id')

    return render(request, "order_history.html", {
        "orders": orders
    })


def apply_coupon(request):
    data = json.loads(request.body)
    code = data.get("coupon")

    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(item.total_price for item in cart_items)

    try:
        coupon = Coupon.objects.get(code=code, active=True)

        # ✅ 1. Minimum order check
        if subtotal < coupon.min_order_amount:
            return JsonResponse({
                "error": f"Minimum order should be ₹{coupon.min_order_amount}"
            })

        # ✅ 2. Calculate discount
        discount = (subtotal * coupon.discount_percent) / 100

        # ✅ 3. Max discount limit
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)

        # ✅ 4. Prevent 100% discount
        if discount >= subtotal:
            discount = subtotal - 1

        # ✅ 5. Shipping logic
        shipping = 0 if subtotal >= 499 else 50

        final_total = subtotal - discount + shipping
        request.session["coupon_code"] = coupon.code
        request.session["discount"] = int(discount)

        return JsonResponse({
            "discount": int(discount),
            "shipping": shipping,
            "final_total": int(final_total)
        })

    except Coupon.DoesNotExist:
        return JsonResponse({"error": "Invalid Coupon"})
    
    
def remove_coupon(request):
    request.session.pop("coupon_code", None)
    request.session.pop("discount", None)

    return JsonResponse({"success": True})

def clear_address(request):
    keys =[
        "saved_name",
        "saved_phone",
        "saved_pincode",
        "saved_city",
        "saved_state",
        "saved_address1",
        "saved_address2",
        "saved_landmark"
    ]

    for key in keys:
        if key in request.session:
            del request.session[key]

    return JsonResponse({"success": True})


@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    items = order.items.all()

    # original subtotal
    subtotal = sum(item.total for item in items)

    # final price from DB
    final_total = order.total_price

    # calculate discount
    discount = subtotal - final_total

    # shipping
    shipping = 0 if subtotal > 500 else 40

    return render(request, "order_detail.html", {
        "order": order,
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "discount": discount,
        "final_total": final_total
    })
@login_required
def cancel_order(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)

    order.status = "cancelled"
    order.save()

    return redirect("order_history")



def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            # 👉 Here you can later add email sending logic
            messages.success(request, "Password reset link sent to your email")

            return redirect("home")

        except User.DoesNotExist:
            messages.error(request, "Email not registered")

    return render(request, "forgot_password.html")




def download_receipt(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.all()

    shipping = 40
    subtotal = order.total_price - shipping

    seal_path = os.path.join(settings.BASE_DIR, 'static/images/seal.png')
    html_string = render_to_string('receipt.html', {
        'order': order,
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'seal_path': seal_path,
    })

    # ✅ HANDLE MISSING xhtml2pdf
    if not pisa:
        return HttpResponse("PDF feature temporarily disabled", status=200)

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)

    if pdf.err:
        return HttpResponse("Error generating PDF", status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{order.id}.pdf"'

    return response
@login_required
def user_settings(request):

    profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        # ✅ UPDATE PROFILE
        if action == "update":
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            address1 = request.POST.get("address1")
            address2 = request.POST.get("address2")
            city = request.POST.get("city")
            state = request.POST.get("state")
            pincode = request.POST.get("pincode")

            # 🔴 REQUIRED VALIDATION
            if not name or not phone or not address1 or not city or not pincode:
                messages.error(request, "All fields except Address Line 2 are required")
                return redirect("user_settings")

            # 🔴 PHONE VALIDATION (10 digits)
            if not re.match(r'^\d{10}$', phone):
                messages.error(request, "Phone number must be 10 digits")
                return redirect("user_settings")

            # 🔴 PINCODE VALIDATION (6 digits)
            if not re.match(r'^\d{6}$', pincode):
                messages.error(request, "Pincode must be 6 digits")
                return redirect("user_settings")

            # 🔴 NAME VALIDATION
            if len(name) < 3:
                messages.error(request, "Name must be at least 3 characters")
                return redirect("user_settings")

            # 🔴 SAVE IF ALL VALID
            profile.full_name = name
            profile.phone = phone
            profile.address_line1 = address1
            profile.address_line2 = address2
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            profile.save()

            messages.success(request, "Profile updated successfully")

        # ❌ DELETE ACCOUNT
        elif action == "delete":
            password = request.POST.get("password")

            user = authenticate(username=request.user.username, password=password)

            if user:
                user.delete()
                return redirect("home")

    return render(request, "settings.html", {"profile": profile})



@login_required
def delete_account(request):

    if request.method == "POST":
        password = request.POST.get("password")

        user = authenticate(username=request.user.username, password=password)

        if user:
            request.user.delete()
            return redirect("home")

    return render(request, "user/delete.html")



@login_required
def change_password(request):
    if request.method == "POST":
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        user = request.user

        # 🔴 check current password
        if not user.check_password(current):
            messages.error(request, "Current password is wrong")
            return redirect("change_password")

        # 🔴 check new password match
        if new != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("change_password")

        # 🔴 update password
        user.set_password(new)
        user.save()

        # keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully")
        return redirect("user_settings")

    return render(request, "change_password.html")

def faq(request):
    return render(request, "faq.html")



def contact(request):
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # ✅ Save to DB (we'll create model next)
            from .models import Contact
            Contact.objects.create(name=name, email=email, message=message)

            # ✅ Send Email
            send_mail(
                subject=f"New Contact from {name}",
                message=message,
                from_email=email,
                recipient_list=["your_email@gmail.com"],  # change this
            )

            return render(request, "contact.html", {
                "form": ContactForm(),
                "success": "Message sent successfully"
            })

    return render(request, "contact.html", {"form": form})
def about(request):
    return render(request, "about.html")






@admin_required
def admin_dashboard(request):

    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    today = timezone.now().date()

    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(created_at__date=today).aggregate(
        Sum('total_price')
    )['total_price__sum'] or 0

    # 📊 Orders per day
    orders_by_date = (
        Order.objects
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    dates = [str(item['date']) for item in orders_by_date]
    counts = [item['count'] for item in orders_by_date]
    # ⚠️ Low stock products
    low_stock_products = Product.objects.filter(stock__lt=5)

    # 📦 Status counts
    placed = Order.objects.filter(status="placed").count()
    shipped = Order.objects.filter(status="shipped").count()
    delivered = Order.objects.filter(status="delivered").count()
    cancelled = Order.objects.filter(status="cancelled").count()
    total_orders = placed + shipped + delivered + cancelled

    return render(request, "admin/dashboard.html", {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "dates": dates,
        
        "counts": counts,
        "low_stock_products": low_stock_products,

    # 🔥 NEW
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "placed": placed,
        "shipped": shipped,
        "delivered": delivered,
        "cancelled": cancelled,
        })


def admin_orders(request):
    orders = Order.objects.all().order_by("-id")

    filter_type = request.GET.get("filter")

    if filter_type == "today":
        today = timezone.now().date()
        orders = orders.filter(created_at__date=today)

    elif filter_type == "week":
        last_week = timezone.now() - timedelta(days=7)
        orders = orders.filter(created_at__gte=last_week)

    start = request.GET.get("start")
    end = request.GET.get("end")

    if start and end:
        orders = orders.filter(created_at__date__range=[start, end])

    status = request.GET.get("status")

    if status:
        orders = orders.filter(status=status)

    return render(request, "admin/orders.html", {"orders": orders})

def update_order_status(request, id):
    order = get_object_or_404(Order, id=id) 
    if request.method == "POST": 
        new_status = request.POST.get("status") 
        order.status = new_status 
        order.save() 
    return redirect("admin_orders")

@admin_required
def admin_products(request):
    products = Product.objects.all().order_by("-id")
    return render(request, "admin/products.html", {"products": products})







@admin_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect("admin_products")
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    return render(request, "admin/add_product.html", {
        "form": form, 
        "categories": categories
    })

@admin_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("admin_products")
    else:
        form = ProductForm(instance=product)
    
    categories = Category.objects.all()
    return render(request, "admin/edit_product.html", {
        "form": form,
        "product": product,
        "categories": categories
    })
    
@admin_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect("admin_products")


@admin_required
def admin_users(request):
    users = User.objects.all()

    return render(request, "admin/users.html", {
        "users": users
    })
    


def delete_user(request, id):
    if request.method == "POST":
        password = request.POST.get("admin_password")

        if not request.user.check_password(password):
            messages.error(request, "Wrong password!")
            return redirect('admin_users')

        target_user = get_object_or_404(User, id=id)

        if target_user == request.user:
            messages.error(request, "You cannot delete your own account!")
            return redirect('admin_users')

        target_user.delete()
        messages.success(request, "User deleted successfully!")

    return redirect('admin_users')


@login_required
def add_testimonial(request):
    if request.user.is_superuser:
        return redirect("home")  # block admin

    if request.method == "POST":
        message = request.POST.get("message")
        rating = request.POST.get("rating")
        image = request.FILES.get("image")

        Testimonial.objects.create(
            name=request.user.username,
            message=message,
            rating=rating,
            image=image
        )

        return redirect("home")
    
from .models import Category
from django.shortcuts import render, redirect

def manage_categories(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            return redirect('manage_categories')

    categories = Category.objects.all()
    return render(request, 'admin/manage_categories.html', {'categories': categories})

def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('manage_categories')