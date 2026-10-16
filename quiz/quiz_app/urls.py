from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('',views.register,name='register'),
    path('login/',views.login,name='login'),
    # path('dashboard/',views.dashboard,name='dashboard'),

    # path('quizzes/', views.quiz_list, name='quiz_list'),
    # path('quizzes/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    # path('quizzes/<int:pk>/start/', views.quiz_start, name='quiz_start'),
    
    # path('attempts/', views.attempt_history, name='attempt_history'),
    # path('attempts/<int:pk>/', views.attempt_take, name='attempt_take'),
    # path('attempts/<int:pk>/result/', views.attempt_result, name='attempt_result'),

    
]