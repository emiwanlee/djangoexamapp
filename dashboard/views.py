from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from subjects.models import Subject
from exams.models import Exam, ExamAttempt, Subscription
from exams.services.scoring import get_weak_topics


@login_required
def home(request):
    sub, _ = Subscription.objects.get_or_create(user=request.user)
    context = {
        "subject_count": Subject.objects.count(),
        "available_exams": Exam.objects.filter(is_published=True).count(),
        "my_attempts": ExamAttempt.objects.filter(student=request.user).order_by("-started_at")[:5],
        "weak_topics": get_weak_topics(request.user),
        "subscription": sub,
    }
    return render(request, "dashboard/home.html", context)
