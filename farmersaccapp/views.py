from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import AllUser
from .decorators import admin_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings


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
