from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from .models import AllUser , FarmerProfile ,BuyerProfile
from .decorators import admin_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from products.models import Product 
from .decorators import farmer_required
from django.views.decorators.http import require_POST
from buyersapp.models import BuyerBuyPrice
from trading.models import FarmerNotification

def home(request):
    return render(request, "user/home.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        role = role.lower() if role else role

        # 🔒 BASIC VALIDATIONS
        if password != confirm_password:
            return render(request, "user/register.html", {
                "error": "Passwords do not match"
            })

        if AllUser.objects.filter(username=username).exists():
            return render(request, "user/register.html", {
                "error": "Username already exists"
            })

        if AllUser.objects.filter(email=email).exists():
            return render(request, "user/register.html", {
                "error": "Email already registered"
            })

        if role == "admin":
            return render(request, "user/register.html", {
                "error": "Admin registration not allowed"
            })

        # ✅ CREATE USER
        user = AllUser.objects.create(
            username=username,
            email=email,
            phone=phone,
            password=make_password(password),
            role=role,
            is_active=True
        )

        # 🔹 BUYER FLOW
        if role == "buyer":
            shop_name = request.POST.get("shop_name")
            gst_number = request.POST.get("gst_number")

            if not shop_name or not gst_number:
                return render(request, "user/register.html", {
                    "error": "Shop name and GST number are required for buyers"
                })

            BuyerProfile.objects.create(
                user=user,
                business_name=shop_name,
                gst_number=gst_number,
                is_exporter=False
            )

            user.is_approved = False
            user.save()

            return render(request, "user/login.html", {
                "success": "Registration successful. Waiting for admin approval."
            })

        # 🔹 FARMER FLOW
        user.is_approved = True
        user.save()

        return redirect("login")

    return render(request, "user/register.html")




def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = AllUser.objects.get(username=username)
        except AllUser.DoesNotExist:
            return render(request, "user/login.html", {
                "error": "User Doesn't Exist! Please Register"
            })

        if not check_password(password, user.password):
            return render(request, "user/login.html", {
                "error": "Invalid credentials"
            })

        # 🚫 BLOCK UNAPPROVED BUYERS
        if user.role == "buyer" and not user.is_approved:
            return render(request, "user/login.html", {
                "error": "Your account is pending admin approval"
            })

        # ✅ SESSION LOGIN (ONLY AFTER APPROVAL CHECK)
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["role"] = user.role

        # 📧 SEND LOGIN EMAIL
        send_mail(
            subject="Login Alert – Farmer Homes",
            message=f"""
            Hello {user.username},

            You have successfully logged into Farmer Homes.

            Role: {user.role}
            Time: Just now

            If this was not you, please contact support immediately.

            – Farmer Homes Team
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True
        )

        # 🔀 ROLE-BASED REDIRECT
        if user.role == "admin":
            return redirect("admin_dashboard")
        elif user.role == "farmer":
            return redirect("user_dashboard")
        else:
            return redirect("buyer_dashboard")

    return render(request, "user/login.html")



@admin_required
def admin_dashboard(request):
    if request.session.get("role") != "admin":
        return redirect("login")

    total_users = AllUser.objects.count()
    total_farmers = AllUser.objects.filter(role="farmer").count()
    total_buyers = AllUser.objects.filter(role="buyer").count()
    total_products = Product.objects.count()

    recent_users = AllUser.objects.order_by("-created_at")[:5]

    context = {
        "total_users": total_users,
        "total_farmers": total_farmers,
        "total_buyers": total_buyers,
        "total_products": total_products,
        "recent_users": recent_users,
    }

    return render(request, "admin/dashboard.html", context)


@admin_required
def admin_pending_buyers(request):
    buyers = BuyerProfile.objects.select_related("user").filter(
        user__role="buyer",
        user__is_approved=False,
        user__is_active=True
    )

    return render(request, "admin/pending_buyers.html", {
        "buyers": buyers
    })


@admin_required
def approve_buyer(request, user_id):
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    user.is_approved = True
    user.save()
    return redirect("admin_pending_buyers")


@admin_required
@require_POST
def reject_buyer(request, user_id):
    user = get_object_or_404(AllUser, id=user_id, role="buyer")

    user.is_active = False
    user.is_approved = False
    user.rejection_reason = request.POST.get("reason")
    user.save()

    return redirect("admin_pending_buyers")


@admin_required
@require_POST
def admin_delete_user(request, user_id):
    if request.session.get("role") != "admin":
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id)

    if user.role == "admin":
        return redirect("admin_users")

    user.delete()
    return redirect("admin_users")



def userlogout(request):
    logout(request)
    return redirect('home')


@farmer_required
def user_dashboard(request):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="farmer")
    farmer = get_object_or_404(FarmerProfile, user=user)

    notifications = FarmerNotification.objects.filter(
        farmer=farmer
    ).order_by("-created_at")

    unread_count = FarmerNotification.objects.filter(
        farmer=farmer,
        is_read=False
    ).count()

    return render(request, "user/user_dashboard.html", {
        "username": user.username,
        "notifications": notifications,
        "unread_count": unread_count
    })

# FORGOT PASSWORD
# ===============================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = AllUser.objects.get(email=email, is_active=True)
        except AllUser.DoesNotExist:
            return render(request, "user/forgot_password.html", {
                "error": "Email not registered"
            })

        # generate secure token
        token = get_random_string(40)
        user.reset_token = token
        user.reset_token_created = timezone.now()
        user.save()

        reset_link = (
            f"http://127.0.0.1:8000/"
            f"reset-password/{user.id}/{token}/"
        )

        send_mail(
            subject="Reset your Smart Agriculture password",
            message=f"""
            Hello {user.username},

            You requested to reset your password.

            Click the link below:
            {reset_link}

            If you did not request this, ignore this email.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return render(request, "user/forgot_password.html", {
            "success": "Password reset link sent to your email"
        })

    return render(request, "user/forgot_password.html")


# ===============================
# RESET PASSWORD
# ===============================
def reset_password(request, user_id, token):
    try:
        user = AllUser.objects.get(
            id=user_id,
            reset_token=token,
            is_active=True
        )
    except AllUser.DoesNotExist:
        return render(request, "user/reset_password.html", {
            "error": "Invalid or expired reset link"
        })

    # Optional: token expiry (30 min)
    if user.reset_token_created:
        elapsed = timezone.now() - user.reset_token_created
        if elapsed.total_seconds() > 1800:
            return render(request, "user/reset_password.html", {
                "error": "Reset link expired"
            })

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            return render(request, "user/reset_password.html", {
                "error": "Passwords do not match"
            })

        user.password = make_password(password)
        user.reset_token = None
        user.reset_token_created = None
        user.save()

        return redirect("login")

    return render(request, "user/reset_password.html")


def admin_users(request):
    # 🔒 custom session check
    if request.session.get("role") != "admin":
        return redirect("login")

    users = AllUser.objects.all()
    return render(request, "admin/users.html", {"users": users})


@farmer_required
def farmer_profile(request):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id)

    # ✅ ensures farmer profile always exists
    farmer, created = FarmerProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        farmer.village = request.POST.get("village")
        farmer.district = request.POST.get("district")
        farmer.state = request.POST.get("state")
        farmer.soil_type = request.POST.get("soil_type")
        farmer.farm_area_acres = request.POST.get("farm_area_acres")
        farmer.bank_account_number = request.POST.get("bank_account_number")
        farmer.ifsc_code = request.POST.get("ifsc_code")


        # 📍 location fields
        lat = request.POST.get("latitude")
        lng = request.POST.get("longitude")

        if lat:
            farmer.latitude = float(lat)
        if lng:
            farmer.longitude = float(lng)

        farmer.save()

    return render(request, "user/profile.html", {"farmer": farmer})



def compare_buyers(request, product_id):
    prices = BuyerBuyPrice.objects.filter(
        product_id=product_id,
        is_active=True
    ).order_by('-price_per_unit')

    return render(request, "farmer/compare_buyers.html", {
        "prices": prices
    })
