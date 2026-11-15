from django.db import models
from django.conf import settings
from datetime import date


class Exam(models.Model):
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="exams"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    pass_mark = models.PositiveIntegerField(default=50)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    topic = models.ForeignKey(
        "subjects.Topic", on_delete=models.SET_NULL, null=True, blank=True
    )
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:60]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student} - {self.exam}"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)


class TopicPerformance(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_perf"
    )
    topic = models.ForeignKey("subjects.Topic", on_delete=models.CASCADE)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "topic")

    @property
    def accuracy(self):
        if self.total_questions == 0:
            return 0
        return round(self.correct_answers / self.total_questions * 100, 1)

    def __str__(self):
        return f"{self.student} · {self.topic} · {self.accuracy}%"


class AIGeneratedQuestion(models.Model):
    topic = models.ForeignKey(
        "subjects.Topic", on_delete=models.CASCADE, related_name="ai_questions"
    )
    question_text = models.TextField()
    choices = models.JSONField()
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:60]


class PracticeSession(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey("subjects.Topic", on_delete=models.CASCADE)
    questions = models.ManyToManyField(AIGeneratedQuestion)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} · {self.topic} · {self.score}/{self.total}"


class Subscription(models.Model):
    PLAN_CHOICES = [("free", "Free"), ("pro", "Pro")]
    FREE_DAILY_LIMIT = 5

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")
    ai_questions_used_today = models.PositiveIntegerField(default=0)
    last_reset = models.DateField(default=date.today)
    stripe_customer_id = models.CharField(max_length=100, blank=True)

    def reset_if_needed(self):
        if self.last_reset < date.today():
            self.ai_questions_used_today = 0
            self.last_reset = date.today()
            self.save(update_fields=["ai_questions_used_today", "last_reset"])

    def can_use_ai(self, count=1):
        if self.plan == "pro":
            return True
        self.reset_if_needed()
        return self.ai_questions_used_today + count <= self.FREE_DAILY_LIMIT

    def __str__(self):
        return f"{self.user} ({self.plan})"