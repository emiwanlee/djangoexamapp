from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Exam, ExamAttempt, AttemptAnswer
from .services.scoring import update_topic_performance


@login_required
def exam_list(request):
    exams = Exam.objects.filter(is_published=True)
    return render(request, "exams/list.html", {"exams": exams})


@login_required
def start_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk, is_published=True)
    attempt = ExamAttempt.objects.create(exam=exam, student=request.user)
    return redirect("take_exam", attempt_id=attempt.id)


@login_required
def take_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student=request.user)
    if attempt.submitted_at:
        return redirect("exam_result", attempt_id=attempt.id)

    if request.method == "POST":
        score = 0
        for question in attempt.exam.questions.all():
            choice_id = request.POST.get(f"question_{question.id}")
            if not choice_id:
                continue
            choice = question.choices.get(pk=choice_id)
            AttemptAnswer.objects.create(
                attempt=attempt, question=question,
                selected_choice=choice, is_correct=choice.is_correct,
            )
            if choice.is_correct:
                score += question.marks

        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.save()
        update_topic_performance(attempt)
        return redirect("exam_result", attempt_id=attempt.id)

    return render(request, "exams/take.html", {"attempt": attempt})


@login_required
def exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student=request.user)
    return render(request, "exams/result.html", {"attempt": attempt, "weak_topics": []})