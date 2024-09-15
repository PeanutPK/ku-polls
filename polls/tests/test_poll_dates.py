"""Test cases for the poll dates function is_published."""
import datetime

from django.test import TestCase
from django.utils import timezone
from polls.models import Question


def create_question(question_text, days):
    """
    Return a Question object with given text and publication date.

    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionPollDatesTests(TestCase):
    """Test question availability due to the date of the poll."""

    def test_is_published_past(self):
        """Test the published question and ended question."""
        question = create_question(question_text="Past question.", days=-5)
        self.assertTrue(question.is_published())

        question_ended = create_question(question_text="Ended question.",
                                         days=-5)
        question_ended.end_date = timezone.now() + datetime.timedelta(days=-1)
        self.assertTrue(question.is_published())

    def test_is_published_present(self):
        """Test that a question is published recently."""
        question = Question(question_text="Present question.")
        self.assertTrue(question.is_published())

    def test_is_published_future(self):
        """Test for question that is not yet publish."""
        question = create_question(question_text="Future question.", days=5)
        self.assertFalse(question.is_published())
