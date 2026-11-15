from django.urls import path
from . import views

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("<int:pk>/start/", views.start_exam, name="start_exam"),
    path("attempt/<int:attempt_id>/", views.take_exam, name="take_exam"),
    path("attempt/<int:attempt_id>/result/", views.exam_result, name="exam_result"),
]