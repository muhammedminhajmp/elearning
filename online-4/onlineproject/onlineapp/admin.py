from django.contrib import admin
from .models import Course, Module, Lesson, LessonResource, Question, Answer

class AnswerAdmin(admin.StackedInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(LessonResource)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
