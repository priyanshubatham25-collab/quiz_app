from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate
from .forms import  RegistrationForm
from django.contrib import messages
from .forms import LoginForm


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
            form.get_user()
            login(request)
            messages.success(request,"login sucessfully")
            return redirect('dashboard')
          else:
            form =LoginForm()
            messages.error(request,"Invalid username or password!")
              
              
     else:
        form =LoginForm()
        messages.error(request,"Invalid username or password!")
          
     return render(request,'login_form.html',{'form': form})    
                
def dashboard(request):
    return render('dashboard.html')