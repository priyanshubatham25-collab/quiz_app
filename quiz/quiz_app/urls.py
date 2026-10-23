from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [

    # Authentication
    path('', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    # Quiz
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('quiz_start/<int:pk>/',views.quiz_start, name='quiz_start'),
    path('quiz_result/<int:pk>/', views.quiz_result, name='quiz_result'),
    path('categories/', views.categories, name='categories'),
    path('attempts/', views.attempts, name='attempts'),
]