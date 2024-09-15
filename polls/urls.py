"""Urls path for /polls/."""
from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    # /polls/
    path("", views.IndexView.as_view(), name="index"),
    # /polls/number/detail/
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # /polls/number/results/
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # /polls/number/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
    # /polls/number/reset/
    path("<int:question_id>/reset/", views.reset_vote, name="reset"),
]
