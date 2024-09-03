from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Question, Choice, Vote


class IndexView(generic.ListView):
    """Displays the home page of the site with all the polls."""
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Returns the last five published questions.
        (not including those set to be in the future)
        Q is for making that query optional.
        """
        return Question.objects.filter(pub_date__lte=timezone.now()
                                       ).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """Display the choices for a poll and allow voting."""
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def dispatch(self, request, *args, **kwargs):
        """
        Try to get a question object, except error 404;
        then it will redirect to index page with response 302.
        """
        try:
            self.object = self.get_object()
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            # Temporary redirect to another page if the object is not found
            messages.error(request, f"Question {kwargs['pk']} does not exist.")
            return redirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.is_published():
        messages.error(request, "This question has not published yet.")
        return render(request, 'polls/detail.html',
                      {
                          "question": question,
                      }, )

    if not question.can_vote():
        messages.error(request, "Voting is not allowed for this question.")
        return HttpResponseRedirect(reverse('polls:index'))

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "Please select a choice")
        return render(request,
                      'polls/detail.html',
                      {
                          "question": question,
                      },
                      )
    # USer variable
    current_user = request.user
    # Get the user's vote
    try:
        # user has a vote for this question
        vote = current_user.vote_set.get(choice=selected_choice)
        vote.choice = selected_choice
        messages.success(request, f"Your vote has updated to {selected_choice.choice_text}")
        vote.save()
    except Vote.DoesNotExist:
        # user dosn't have a vote for this question
        vote = Vote.objects.create(user=current_user, choice=selected_choice)
        messages.success(request, f"You have voted for {selected_choice.choice_text}")

    return HttpResponseRedirect(
        reverse("polls:results", args=(question.id,)))
