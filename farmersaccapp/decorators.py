from django.shortcuts import redirect
from .models import AllUser

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")

        if request.session.get("role") != "admin":
            return redirect("login")

        return view_func(request, *args, **kwargs)
    return wrapper

def farmer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")

        if request.session.get("role") != "farmer":
            return redirect("login")

        return view_func(request, *args, **kwargs)
    return wrapper

def buyer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "buyer":
            return redirect("login")

        user = AllUser.objects.get(id=request.session["user_id"])
        if not user.is_approved:
            return redirect("login")

        return view_func(request, *args, **kwargs)
    return wrapper

