from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from sales.views import *
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_approved = False   # important
            user.save()

            messages.success(request, "Registered! Wait for admin approval.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'login.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_approved:
                return HttpResponse("Wait for admin approval")

            login(request, user)
            return redirect('dashboard')
        else:
            return HttpResponse("Invalid credentials")

    return render(request, 'login.html')



 
def dashboard(request):
    if request.user.role == 'salesman':
        return redirect('/inventory/')
    elif request.user.role == 'inventory':
        return redirect('sales:manager_dashboard')
    elif request.user.role == 'sales_manager':
        return redirect("sales:sales_manager_dashboard")

    return HttpResponse("Unknown Role")

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')