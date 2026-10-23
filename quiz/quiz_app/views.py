from django.http import request
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout,login as auth_login
from django.utils import timezone
from .forms import  RegistrationForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.db.models import F, Avg, ExpressionWrapper, Prefetch, fields
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

@login_required(login_url='login')
def quiz_list(request):
     return render(request,'quiz_list.html')



@login_required(login_url='login')
def quiz_start(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    questions = quiz.questions.prefetch_related('choices').all()
    total_questions = questions.count()

    if request.method == 'GET':

        # Check karo ki session mein active attempt hai ya nahi
        attempt_id = request.session.get(
            f'active_attempt_{quiz.id}'
        )

        attempt = None

        if attempt_id:
            attempt = Attempt.objects.filter(
                pk=attempt_id,
                user=request.user,
                quiz=quiz,
                finished_at__isnull=True
            ).first()

        # Sirf tab naya attempt banao jab active attempt nahi hai
        if attempt is None:
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

    if request.method == 'POST':
        answered = any(request.POST.get(f'question_{question.id}')
        for question in questions
)

        if not answered:
             return redirect('quiz_start', pk=quiz.pk)

        # Active attempt ki ID session se lena
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

        # Har question ka answer check karna
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')

            if selected_choice_id:
                selected_choice = question.choices.filter( pk=selected_choice_id).first()

                if selected_choice.is_correct:
                    score += 1

        # Same attempt ko update karna
        attempt.score = score
        attempt.total = total_questions
        attempt.finished_at = timezone.now()
        attempt.save()

        # Session se active attempt remove karna
        request.session.pop(f'active_attempt_{quiz.id}', None )

        # Percentage calculate karna
        percentage = ((score / total_questions) * 100
            if total_questions > 0 else 0
        )

        # Pass ya fail check karna
        passed = percentage >= quiz.pass_percentage
        
        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions,
            'percentage':percentage  ,
            'passed': passed,
        })
    else:
        return redirect('quiz_start', pk=quiz.pk)




@login_required(login_url='login')
def categories(request):
     return render(request,'categories.html')   

@login_required(login_url='login')
def attempts(request):
    user_attempts_prefetch = Prefetch(
        'attempts',
        queryset=Attempt.objects.filter(
            user=request.user, 
            finished_at__isnull=False  # Only fetch successfully finished runs
        ).order_by('-start_at'),
        to_attr='user_specific_attempts' 
    )
    quizzes = Quiz.objects.filter(
        attempts__user=request.user,
        attempts__finished_at__isnull=False
    ).prefetch_related(user_attempts_prefetch).distinct()

    return render(request, 'attempts.html', {'quizzes': quizzes})


@login_required(login_url='login')
def leaderboard(request):
    all_completed_attempts = Attempt.objects.filter(
        finished_at__isnull=False
    ).annotate(
        duration_secs=ExpressionWrapper(
            F('finished_at') - F('start_at'),
            output_field=fields.DurationField()
        )
    ).order_by('-score', 'duration_secs', 'start_at') 
    best_attempts_by_user = {}
    for attempt in all_completed_attempts:
        user_id = attempt.user_id
        
        if user_id not in best_attempts_by_user:
            best_attempts_by_user[user_id] = attempt

    sorted_global_list = sorted(
        best_attempts_by_user.values(),
        key=lambda x: (-x.score, x.duration_seconds)
    )
    leaderboard_positions = []
    current_user_rank = None

    for index, attempt in enumerate(sorted_global_list):
        rank_position = index + 1
        if rank_position <= 4:
            leaderboard_positions.append({
                'rank': rank_position,
                'username': attempt.user.username,
                'quiz_title': attempt.quiz.title,
                'score': attempt.score,
                'total': attempt.total,
                'time_display': attempt.duration_display
            })
        if attempt.user == request.user:
            current_user_rank = rank_position

    context = {
        'leaderboard': leaderboard_positions,
        'current_user_rank': current_user_rank
    }
    return render(request, 'leaderboard.html', context)
