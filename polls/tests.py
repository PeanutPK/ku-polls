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


class QuestionIndexViewTests(TestCase):
    """
    Tests for `polls.views`
    """

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        Returns a 404 not found error message.
        """
        future_question = create_question(question_text="Future Question.",
                                          days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question], )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question2, question1], )

    def test_is_published(self):
        """
        Test for is_published function.
        1. Question1 for the past question that already ends.
        2. Question2 for the default question (present time).
        3. Question3 for the future question.
        """
        question1 = create_question(question_text="Past question.", days=-5)
        question1.end_date = timezone.now() + datetime.timedelta(days=-1)
        self.assertTrue(question1.is_published())

        question2 = Question(question_text="Present question.")
        self.assertTrue(question2.is_published())

        question3 = create_question(question_text="Future question.", days=5)
        self.assertFalse(question3.is_published())

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
