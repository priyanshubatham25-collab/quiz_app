from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('quiz_list/',views.quiz_list,name='quiz_list'),
    path('quiz_details/',views.quiz_details,name='quiz_details'),
    path('categories/' ,views.categories, name='categories')
    
]