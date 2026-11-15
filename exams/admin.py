from django.contrib import admin
from .models import (
    Exam, Question, Choice, ExamAttempt, AttemptAnswer,
    TopicPerformance, AIGeneratedQuestion, PracticeSession, Subscription,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "exam", "topic", "marks", "order")
    list_filter = ("exam", "topic")
    inlines = [ChoiceInline]


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "is_published", "duration_minutes")
    list_filter = ("subject", "is_published")
    inlines = [QuestionInline]


for m in [Choice, ExamAttempt, AttemptAnswer, TopicPerformance,
          AIGeneratedQuestion, PracticeSession, Subscription]:
    admin.site.register(m)




