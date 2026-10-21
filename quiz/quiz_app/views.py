from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout,login as auth_login
from .forms import  RegistrationForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from .models import Attempt,Question ,Choice,Category,Quiz 
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




@login_required(login_url='login')
def dashboard(request):
    quizzes = Quiz.objects.filter(is_published=True)
    return render(request, 'dashboard.html', {'quizzes': quizzes})

@login_required(login_url='login')
def quiz_list(request):
     return render(request,'quiz_list.html')



login_required(login_url='login')
def quiz_start(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('choices').all()

    return render(request, 'quiz_details.html', {'quiz': quiz,'questions': questions})




@login_required(login_url='login')
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz,pk=pk)
    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()

        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                selected_choice = Choice.objects.get(id=selected_choice_id)
                if selected_choice.is_correct:
                    score += 1

        # Save the attempt
        Attempt.objects.create(user=request.user, quiz=quiz, score=score)

        return render(request, 'quiz_result.html', { 'quiz': quiz, 'score': score, 'total_questions': total_questions })
    return render(request, 'quiz_result.html')


@login_required(login_url='login')
def categories(request):
     return render(request,'categories.html')   

@login_required(login_url='login')
def attempts(request):
    quizzes = Quiz.objects.filter(is_published=True).prefetch_related('attempts', 'questions')
    return render(request, 'attempts.html', {'quizzes': quizzes})
    
