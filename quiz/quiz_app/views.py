from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate
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
                
# @login_required
# def dashboard(request):
#     finished_qs = Attempt.objects.filter(user=request.user, finished_at__isnull=False).select_related('quiz')
#     finished = list(finished_qs[:200])
#     percentages = [a.percentage for a in finished]
#     context = {
#         'attempt_count': finished_qs.count(),
#         'average': round(sum(percentages) / len(percentages), 1) if percentages else None,
#         'best': max(percentages) if percentages else None,
#         'passed_count': sum(1 for a in finished if a.passed),
#         'recent': finished[:5],
#         'in_progress': Attempt.objects.filter(user=request.user, finished_at__isnull=True).select_related('quiz'),
#         'featured': published_quizzes().order_by('-created_at')[:3],
#     }
#     return render(request, 'quiz/dashboard.html', context)





# def published_quizzes():
#     """Published quizzes that have at least one question."""
#     return (Quiz.objects.filter(is_published=True)
#             .select_related('category')
#             .annotate(question_total=Count('questions', distinct=True))
#             .filter(question_total__gt=0))



# @login_required
# def quiz_list(request):
#     q = request.GET.get('q', '').strip()
#     category_id = request.GET.get('category', '').strip()

#     quizzes = published_quizzes()
#     if q:
#         quizzes = quizzes.filter(Q(title__icontains=q) | Q(description__icontains=q))
#     if category_id.isdigit():
#         quizzes = quizzes.filter(category_id=int(category_id))
#     params = request.GET.copy()
#     params.pop('page', None)
#     return render(request, 'quiz_list.html', {
#         'categories': Category.objects.all(),
#         'q': q, 'category_id': category_id,
#         'querystring': params.urlencode(),
#     })


# @login_required
# def quiz_detail(request, pk):
#     quiz = get_object_or_404(published_quizzes(), pk=pk)
#     my_attempts = Attempt.objects.filter(user=request.user, quiz=quiz, finished_at__isnull=False)[:5]
#     in_progress = Attempt.objects.filter(user=request.user, quiz=quiz, finished_at__isnull=True).first()
#     return render(request, 'quiz_detail.html', {
#         'quiz': quiz, 'my_attempts': my_attempts, 'in_progress': in_progress,
#     })


# @login_required
# @require_POST
# def quiz_start(request, pk):
#     quiz = get_object_or_404(published_quizzes(), pk=pk)
#     attempt = Attempt.objects.filter(user=request.user, quiz=quiz, finished_at__isnull=True).first()
#     if attempt is None:
#         attempt = Attempt.objects.create(user=request.user, quiz=quiz, total=quiz.question_total)
#     return redirect('attempt_take', pk=attempt.pk)