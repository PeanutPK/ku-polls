import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from polls.models import Question, Choice
from mysite import settings


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
        Returns a 302-response message to redirect them to index page.
        """
        future_question = create_question(question_text="Future Question.",
                                          days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        self.client.login(username=self.username, password=self.password)
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


"""Tests of authentication."""


class UserAuthTest(TestCase):

    def setUp(self):
        """superclass setUp creates a Client object and
        initializes a test database"""
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can log out using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        response = self.client.get(logout_url)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)
