from collections import defaultdict
from django.db.models import F, FloatField, ExpressionWrapper
from exams.models import TopicPerformance


def update_topic_performance(attempt):
    per_topic = defaultdict(lambda: {"total": 0, "correct": 0})
    for answer in attempt.answers.select_related("question__topic"):
        topic = answer.question.topic
        if not topic:
            continue
        per_topic[topic.id]["total"] += 1
        if answer.is_correct:
            per_topic[topic.id]["correct"] += 1

    for topic_id, stats in per_topic.items():
        perf, _ = TopicPerformance.objects.get_or_create(
            student=attempt.student, topic_id=topic_id
        )
        perf.total_questions += stats["total"]
        perf.correct_answers += stats["correct"]
        perf.save()


def get_weak_topics(student, threshold=60, limit=5):
    return (
        TopicPerformance.objects.filter(student=student, total_questions__gte=1)
        .annotate(
            accuracy_pct=ExpressionWrapper(
                F("correct_answers") * 100.0 / F("total_questions"),
                output_field=FloatField(),
            )
        )
        .filter(accuracy_pct__lt=threshold)
        .select_related("topic__scheme__subject")
        .order_by("accuracy_pct")[:limit]
    )