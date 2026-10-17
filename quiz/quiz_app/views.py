from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout,login as auth_login
from .forms import  RegistrationForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from .models import Attempt, AttemptAnswer, Category, Quiz  
from django.db.models import Count, Q
from django.views.decorators.http import require_POST


def register(request):
    if request.method == "POST":
        form =  RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            login(request)
            messages.success(request,'registration sucessfull 👍!')
            return redirect('login')

        else:
            messages.error(request,"registration failed please try again!")
            return render(request,"registration_form.html",{'form':form})
    else:
        form = RegistrationForm() 
        return render(request,"registration_form.html",{'form': form}) 
    
       
            
def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Login successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")

    else:
        form = LoginForm()

    return render(request, 'login_form.html', {'form': form})

              
def logout_user(request):
        logout(request)
        messages.success(request,"you have been logged out")
        return redirect('login')


def dashboard(request):
    return render(request,'dashboard.html')

def quiz_list(request):
    return render(request,"quiz_list.html")

def quiz_details(request):
    return render(request,"quiz_details.html")