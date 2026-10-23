from django.http import request
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout,login as auth_login
from django.utils import timezone
from .forms import  RegistrationForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, Prefetch, fields
from .models import Attempt ,Choice,Quiz 
from django.views.decorators.http import require_POST
import random



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

            # Har naye login par counters reset
            request.session['completed_count'] = 0
            request.session['learning_started_at'] = (
                timezone.now().timestamp()
            )
            request.session['learning_seconds'] = 0

            messages.success(request, "Login successfully!")
            return redirect('dashboard')

        else:
            messages.error(
                request, "Invalid username or password!"
            )
    else:
        form = LoginForm()

    return render(
        request, 'login_form.html', {'form': form}
    )





# logout view-----------------------
def logout_user(request):
        logout(request)
        messages.success(request,"you have been logged out")
        return redirect('login')





# dashboard view----------------------
@login_required(login_url='login')
def dashboard(request):
    # Total published quizzes
    quizzes = Quiz.objects.filter(is_published=True)

    # Average percentage of completed quizzes
    attempts = Attempt.objects.filter(
        user=request.user,
        finished_at__isnull=False,
        total__gt=0
    )

    percentages = [
        (attempt.score / attempt.total) * 100
        for attempt in attempts
    ]

    percentage = round(
        sum(percentages) / len(percentages), 2
    ) if percentages else 0

    # Total available quizzes
    total_quizzes = quizzes.count()

    # Quizzes completed during current login session
    completed_count = request.session.get(
        'completed_count', 0
    )

    # Learning time in seconds during current login session
    learning_seconds = request.session.get(
        'learning_seconds', 0
    )

    return render(request, 'dashboard.html', {
        'quizzes': quizzes,
        'percentage': percentage,
        'total_quizzes': total_quizzes,
        'completed_count': completed_count,
        'learning_seconds': learning_seconds,
    })


@login_required(login_url='login')
def quiz_list(request):
     return render(request,'quiz_list.html')



@login_required(login_url='login')
def quiz_start(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    # Get all questions for this quiz
    all_questions = list(
        quiz.questions.prefetch_related('choices').all()
    )

    total_questions = min(10, len(all_questions))

    if request.method == 'GET':

        # Check whether an active attempt already exists
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

        # Create a new attempt only if no active attempt exists
        if attempt is None:
            attempt = Attempt.objects.create(
                user=request.user,
                quiz=quiz,
                total=total_questions,
                score=0
            )

            # Select 10 random questions for this attempt
            selected_questions = random.sample(
                all_questions, total_questions
            )

            # Save question IDs so refresh keeps the same questions
            request.session[
                f'quiz_questions_{attempt.id}'
            ] = [q.id for q in selected_questions]

            request.session[
                f'active_attempt_{quiz.id}'
            ] = attempt.id

        else:
            # Retrieve the same questions for the existing attempt
            question_ids = request.session.get(
                f'quiz_questions_{attempt.id}', []
            )

            questions_by_id = {
                q.id: q for q in all_questions
            }

            selected_questions = [
                questions_by_id[qid]
                for qid in question_ids
                if qid in questions_by_id
            ]

            # Fallback if the saved question IDs are missing
            if not selected_questions:
                selected_questions = random.sample(
                    all_questions, total_questions
                )

                request.session[
                    f'quiz_questions_{attempt.id}'
                ] = [q.id for q in selected_questions]

        return render(request, 'quiz_details.html', {
            'quiz': quiz,
            'questions': selected_questions,
            'attempt': attempt,
            'total_questions': len(selected_questions),
        })

    return redirect('quiz_start', pk=quiz.pk)

# quiz_result view----------------------


@login_required(login_url='login')
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        answered = any(
            request.POST.get(f'question_{question.id}')
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
        total_questions = 10

        # Har question ka answer check karna
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

        # Attempt save karna
        attempt.score = score
        attempt.total = total_questions
        attempt.finished_at = timezone.now()
        attempt.save()

        # Isi login session mein completed count badhana
        request.session['completed_count'] = (
            request.session.get('completed_count', 0) + 1
        )

        # Active attempt remove karna
        request.session.pop(
            f'active_attempt_{quiz.id}', None
        )

        # Actual total questions se percentage
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
            'passed': passed,
        })

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
