from django.urls import path
from .views import register, user_login, dashboard, user_logout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', user_login, name='home'),

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),

    # ✅ LOGOUT
    path('logout/', user_logout, name='logout'),

    # ✅ CHANGE PASSWORD (FIXED)
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/change-password-done/'   # ✅ IMPORTANT FIX
    ), name='change_password'),

    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='change_password_done.html'
    ), name='password_change_done'),
]