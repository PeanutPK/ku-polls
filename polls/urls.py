from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    # /polls/
    path("", views.index, name="index"),
    # /polls/number/detail/
    path("<int:question_id>/detail/", views.detail, name="detail"),
    # /polls/number/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # /polls/number/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
