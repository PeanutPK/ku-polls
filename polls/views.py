from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from polls.models import Question, Choice, Vote

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed
import logging

logger = logging.getLogger(__name__)


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
                                       ).order_by("-pub_date")


class DetailView(generic.DetailView):
    """Display the choices for a poll and allow voting."""
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, *args, **kwargs):
        """
        If user vote then show the vote to user in a message and radio checked.
        """
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        question = self.get_object()
        try:
            user_vote = Vote.objects.get(user=current_user,
                                         choice__question=question.id)
            messages.add_message(self.request, messages.INFO,
                                 f"Previously {user_vote}")
        except (KeyError, Vote.DoesNotExist):
            user_vote = None
        context["question"] = question
        context["user_vote"] = user_vote
        return context

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
    # User variable
    current_user = request.user
    # Get the user's vote
    try:
        # user has a vote for this question
        vote = Vote.objects.get(user=current_user, choice__question=question)
        vote.choice = selected_choice
        messages.success(request,
                         f"Your vote has updated to "
                         f"{selected_choice.choice_text}")
        vote.save()
    except Vote.DoesNotExist:
        # user doesn't have a vote for this question
        Vote.objects.create(user=current_user, choice=selected_choice)
        messages.success(request,
                         f"You have voted for {selected_choice.choice_text}")
    logger.info(f"{current_user.username} votes for "
                f"{selected_choice.choice_text} at question {question.id}")
    return HttpResponseRedirect(
        reverse("polls:results", args=(question.id,)))


def signup(request):
    """Register a new user."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data and password input field
            # called 'password1'
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("polls:index")
        else:
            messages.error(request, "Not valid form.")
            return render(request, 'registration/signup.html', {'form': form})
    else:
        # Create a form and display
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def logout_view(request, *args, **kwargs):
    """Logs the user out and redirects to the login page."""
    ip_address = get_client_ip(request)
    logout(request)
    logger.info(f"Logged out from {ip_address}")
    return redirect("login")


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """Logs for the user login success."""
    ip_address = get_client_ip(request)
    logger.info(f'Login user: {user} via ip: {ip_address}')


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    """Logs the user login failed."""
    ip_address = get_client_ip(request)
    logger.warning(f'login failed: {ip_address}')
