from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import AllUser
from .decorators import admin_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string

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

        AllUser.objects.create(
            username=username,
            email=email,
            phone=phone,
            password=make_password(password),
            role=role
        )

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
                "error": "Invalid credentials"
            })

        if not check_password(password, user.password):
            return render(request, "user/login.html", {
                "error": "Invalid credentials"
            })

        # ✅ SESSION LOGIN
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
            return redirect("home")

    return render(request, "user/login.html")


@admin_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

def userlogout(request):
    logout(request)
    return redirect('home')

def user_dashboard(request):
    return render(request, "user/user_dashboard.html")

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
