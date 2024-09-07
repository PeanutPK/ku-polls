import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionVotingTests(TestCase):
    """
    Voting availability test.
    """

    def test_cannot_vote_future_polls(self):
        """
        Can't vote for future polls, and the polls shouldn't be shown.
        """
        question1 = create_question(question_text="Future question1.", days=5)
        question2 = create_question(question_text="Future question2.", days=1)
        response = self.client.get(reverse("polls:index"))
        self.assertFalse(question1.can_vote())
        self.assertFalse(question2.can_vote())
        self.assertContains(response, "No polls are available.")

    def test_cannot_vote_ended_polls(self):
        """
        Can't vote for polls that already ends.
        """
        question = create_question(question_text="Ended question.", days=-1)
        question.end_date = timezone.now() + datetime.timedelta(days=-1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [question])
        self.assertFalse(question.can_vote())

    def test_can_vote_question(self):
        """
        Can vote for currently active questions.
        """
        question = create_question(question_text="Ended question.", days=-1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],
                                 [question])
        self.assertTrue(question.can_vote())
