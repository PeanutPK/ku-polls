"""Models for django MVT structure."""
import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Question model for polls with two attributes.

    1. question_text as the question.
    2. pub_date as the publishing date.
    """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('ended date', blank=True, null=True)

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        """Check whether this question is publicly active."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published?",
    )
    def is_published(self):
        """Return checking whether this question has been published or not."""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """
        Return boolean for checking whether the question is in voting time.

        Checking whether this question is between the voting time.
        """
        now = timezone.now()
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date

    def __str__(self):
        """Display question text when print out the object."""
        return self.question_text


class Choice(models.Model):
    """
    Choice model for polls with three attributes.

    1. Question to define which choice it belongs to.
    2. Choice_text as the choice.
    3. Votes to keep track of the votes this choice has.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """Return number of votes this choice has."""
        return self.vote_set.count()

    def __str__(self):
        """Display the text of the choice when print out the object."""
        return self.choice_text


class Vote(models.Model):
    """Vote model for user to vote for a choice in a poll."""

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return text of the user and their choice."""
        return f"{self.user.username} voted for {self.choice.choice_text}"
