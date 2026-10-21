from django.http import request
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout,login as auth_login
from django.utils import timezone
from datetime import datetime
from .forms import  RegistrationForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from .models import Attempt ,Choice,Quiz 
from django.views.decorators.http import require_POST


# register view---------------------
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
    


# login view------------------------        
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




# logout view-----------------------
def logout_user(request):
        logout(request)
        messages.success(request,"you have been logged out")
        return redirect('login')





# dashboard view----------------------
@login_required(login_url='login')
def dashboard(request):
    quizzes = Quiz.objects.filter(is_published=True)
    return render(request, 'dashboard.html', {'quizzes': quizzes})


# quiz_list view----------------------
def quiz_list(request):
     return render(request,'quiz_list.html')


@login_required(login_url='login')
def quiz_start(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    questions = quiz.questions.prefetch_related('choices').all()
    total_questions = questions.count()

    if request.method == 'GET':
        attempt = Attempt.objects.create(
            user=request.user,
            quiz=quiz,
            total=total_questions,
            score=0
        )

        request.session[f'active_attempt_{quiz.id}'] = attempt.id

        return render(request, 'quiz_details.html', {
            'quiz': quiz,
            'questions': questions,
            'attempt': attempt,
            'total_questions': total_questions,
        })

    return redirect('quiz_start', pk=quiz.pk)


# quiz_result view----------------------
@login_required(login_url='login')
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('choices').all()

    if request.method != 'POST':
        return redirect('quiz_start', pk=quiz.pk)

    # Find the attempt created when the quiz started
    attempt_id = request.session.get(
        f'active_attempt_{quiz.id}'
    )

    attempt = get_object_or_404(
        Attempt,
        pk=attempt_id,
        user=request.user,
        quiz=quiz,
        finished_at__isnull=True
    )

    score = 0
    total_questions = questions.count()

    # Check the selected answer for each question
    for question in questions:
        selected_choice_id = request.POST.get(
            f'question_{question.id}'
        )

        if selected_choice_id:
            selected_choice = question.choices.filter(
                pk=selected_choice_id
            ).first()

            if selected_choice and selected_choice.is_correct:
                score += 1

    # Update the SAME attempt record
    total_questions = questions.count()
    attempt.score = score
    attempt.total = total_questions
    attempt.finished_at = timezone.now()
    attempt.save()

    # Remove active attempt from the session
    del request.session[f'active_attempt_{quiz.id}']

    percentage = (
        (score / total_questions) * 100
        if total_questions > 0 else 0
    )

    passed = percentage >= quiz.pass_percentage
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'score': score,
        'total_questions': total_questions,
        'percentage': round(percentage, 2),
        'passed': passed
    })





def categories(request):
     return render(request,'categories.html')   


# attempts views ---------------
@login_required(login_url='login')
def attempts(request):
    attempts = Attempt.objects.select_related(
        'user', 'quiz'
    ).order_by('-start_at')

    return render(request, 'attempts.html', {
        'attempts': attempts
    })
