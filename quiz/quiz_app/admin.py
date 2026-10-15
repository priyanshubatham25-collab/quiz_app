from django.contrib import admin
from django import forms
from django.forms import BaseInlineFormSet

# Register your models here.
from .models import Category, Quiz, Attempt,Choice,Question


class ChoiceInlineFormSet(BaseInlineFormSet):
    """Every question needs at least 2 choices and exactly 1 correct one."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        filled = [f for f in self.forms
                  if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        if len(filled) < 2:
            raise forms.ValidationError('Add at least 2 choices.')
        if sum(1 for f in filled if f.cleaned_data.get('is_correct')) != 1:
            raise forms.ValidationError('Mark exactly ONE choice as correct.')



class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceInlineFormSet
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    fields = ('text', 'order')
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
<<<<<<< HEAD
    list_display = ['name']
=======
    list_display = ('name')
>>>>>>> 26faa9f0ae8b9ed0ebc88102771bb720fbcc5ddf

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display=('title','category', 'time_limit_minutes', 'pass_percentage', 'is_published')
    list_filter = ('category', 'is_published')
<<<<<<< HEAD
    search_fields = ['title']
=======
    search_fields = ('title')
>>>>>>> 26faa9f0ae8b9ed0ebc88102771bb720fbcc5ddf
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmnin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    inlines = [ChoiceInline]

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
<<<<<<< HEAD
    list_display = ('user', 'quiz', 'score', 'total', 'start_at', 'finished_at')
=======
    list_display = ('user', 'quiz', 'score', 'total', 'started_at', 'finished_at')
>>>>>>> 26faa9f0ae8b9ed0ebc88102771bb720fbcc5ddf
    list_filter = ('quiz',)
