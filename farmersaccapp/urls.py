from django.urls import path
from .import views

urlpatterns = [
    path('',views.home,name="home"),
    path("register/",views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('logout/', views.userlogout, name='logout'),
    path("user dashboard/", views.user_dashboard, name="user_dashboard"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<int:user_id>/<str:token>/', views.reset_password, name='reset_password'),
    path("dashboard/users/", views.admin_users, name="admin_users")

]