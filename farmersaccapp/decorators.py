from django.shortcuts import redirect
from .models import AllUser
from functools import wraps

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
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login")

        user = AllUser.objects.get(id=user_id)
        if user.role != "farmer":
            return redirect("login")

        request.current_user = user   # 🔥 attach once
        return view_func(request, *args, **kwargs)
    return wrapper

def buyer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if not user_id or role != "buyer":
            return redirect("login")

        user = AllUser.objects.get(id=user_id)

        if not user.is_approved:
            return redirect("login")

        # 🔥 Attach buyer user once (JUST LIKE farmer_required)
        request.current_user = user

        return view_func(request, *args, **kwargs)

    return wrapper

