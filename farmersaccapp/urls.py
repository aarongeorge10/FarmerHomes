from django.urls import path
from .import views

urlpatterns = [
    path('',views.home,name="home"),
    path("register/",views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('logout/', views.userlogout, name='logout'),
    path("user dashboard/", views.user_dashboard, name="user_dashboard"),

]